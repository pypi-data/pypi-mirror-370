# -*- coding: utf-8 -*-

import sys
import json
import pathlib
import argparse
import tuxsuite
import tuxsuite.exceptions
import tuxsuite.cli.colors as colors
import tuxsuite.cli.icons as icons

from tuxsuite.utils import error
from tuxsuite.cli.models import Bitbake
from tuxsuite.cli.requests import post, get, apiurl, get_storage
from tuxsuite.cli.utils import (
    LIMIT,
    datediff,
    fetch_next,
    file_or_url,
    format_result,
    wait_for_object,
    is_url,
    get_cb_headers,
    load_build_definition,
    validate_notify_emails,
)


def handle_get(options, _, config):
    ret = get(
        config,
        f"/v1/groups/{config.group}/projects/{config.project}/oebuilds/{options.uid}",
    )
    if ret.status_code != 200:
        raise NotImplementedError()

    oebuild = Bitbake.new(**ret.json())
    if options.json:
        print(oebuild.as_json())
    elif options.json_out:
        options.json_out.write(json.dumps(oebuild.as_dict(), indent=4))
    elif options.list_artifacts:
        path_url = (
            f"{oebuild.download_url}{options.list_artifacts}/"
            if options.list_artifacts is not True
            else oebuild.download_url
        )
        ret = get_storage(config, path_url).json()
        for folder in ret.get("folders", []):
            print(f"📁 {folder['Url'].split('/')[-2]}")
        for file in ret.get("files", []):
            print(f"📄 {file['Url'].split('/')[-1]}")
        if options.download_artifacts:
            tuxsuite.download.download_artifacts(
                config, oebuild, options.download_artifacts, options.list_artifacts, ret
            )
    elif options.download_artifacts:
        tuxsuite.download.download_artifacts(
            config, oebuild, options.download_artifacts
        )
    else:
        print(f"url       : {apiurl(config, oebuild.url())}")
        print(f"project   : {oebuild.project}")
        print(f"uid       : {oebuild.uid}")
        print(f"plan      : {oebuild.plan}")
        if oebuild.waited_by:
            print(
                f"tests     : {', '.join([t.split('#')[1] for t in oebuild.waited_by])}"
            )
        print(f"user      : {oebuild.user}")

        print(f"distro    : {oebuild.distro}")
        print(f"machine   : {oebuild.machine}")
        print(f"container : {oebuild.container}")
        print(f"envsetup  : {oebuild.envsetup}")
        print(f"targets   : {oebuild.targets}")

        if oebuild.provisioning_time:
            print(f"{icons.PROVISIONING} time   : {oebuild.provisioning_time}")
        if oebuild.running_time:
            print(f"{icons.RUNNING} time   : {oebuild.running_time}")

        if oebuild.state == "finished":
            if oebuild.result == "pass":
                icon = icons.PASS
            elif oebuild.result == "error":
                icon = icons.ERROR
            elif oebuild.result == "fail":
                icon = icons.FAIL
            elif oebuild.result == "unknown":
                icon = icons.UNKNOWN
            elif oebuild.result == "canceled":
                icon = icons.CANCELED
            print(f"{icon} time   : {oebuild.finished_time}")
        if oebuild.duration:
            print(f"duration  : {oebuild.duration}")

        print(f"state     : {oebuild.state}")
        color = ""
        if oebuild.result == "pass":
            color = colors.green
        elif oebuild.result == "canceled":
            color = colors.white
        elif oebuild.result in ["error", "fail"]:
            color = colors.red
        elif oebuild.result == "unknown":
            color = colors.purple
        print(f"result    : {color}{oebuild.result}{colors.reset}")

    return 0


def handle_list(options, _, config):
    url = f"/v1/groups/{config.group}/projects/{config.project}/oebuilds"
    ret = get(config, url)
    if ret.status_code != 200:
        raise NotImplementedError()

    oebuilds = [Bitbake.new(**t) for t in ret.json()["results"]]
    n_token = ret.json()["next"]
    if options.json or options.json_out:
        itrs = options.limit // LIMIT
        for _ in range(itrs):
            if not n_token:
                break
            items, n_token = fetch_next(Bitbake, config, url, n_token)
            oebuilds.extend(items)
        if options.json:
            print(json.dumps([b.as_dict() for b in oebuilds[: options.limit]]))
        elif options.json_out:
            options.json_out.write(
                json.dumps([b.as_dict() for b in oebuilds[: options.limit]], indent=4)
            )
    else:
        previous_pt = None
        while True:
            while len(oebuilds) < options.limit and n_token:
                items, n_token = fetch_next(Bitbake, config, url, n_token)
                oebuilds.extend(items)

            if not oebuilds:
                break

            for oebuild in oebuilds[: options.limit]:
                state = oebuild.result if oebuild.state == "finished" else oebuild.state
                state_msg = (
                    (
                        f"{colors.state(oebuild.state, oebuild.result)}{state}{colors.reset}"
                    )
                    if sys.stdout.isatty()
                    else state
                )
                pt = oebuild.provisioning_time
                if pt is None:
                    pt = "....-..-..T..:..:........."
                pt = pt[:-7]
                print(
                    f"{datediff(previous_pt, pt)} {oebuild.uid} [{state_msg}] distro={oebuild.distro}, "
                    f"machine={oebuild.machine}, target={oebuild.targets}"
                )

                previous_pt = pt
            oebuilds = oebuilds[options.limit :]
            if sys.stdout.isatty():
                try:
                    input(
                        "\nPress [ENTER] to see next list of oebuilds, or Ctrl-C to quit:\n"
                    )
                except KeyboardInterrupt:
                    sys.exit(0)
    return 0


def handle_submit(cmdargs, _, config):
    build_definition = cmdargs.build_definition[0]
    data = load_build_definition(build_definition)
    if cmdargs.local_manifest and cmdargs.pinned_manifest:
        error("Either local manifest or pinned manifest to be provided, not both")
    else:
        # either one will be present
        data["manifest_file"] = cmdargs.local_manifest
        data["pinned_manifest"] = cmdargs.pinned_manifest

    cb_headers = None
    if cmdargs.callback_header:
        if not cmdargs.callback:
            error("--callback-header given without a --callback")
        else:
            cb_headers = get_cb_headers(cmdargs.callback_header)

    data["no_cache"] = cmdargs.no_cache
    data["is_public"] = cmdargs.private
    data["callback"] = cmdargs.callback
    data["callback_headers"] = cb_headers
    data["kas_override"] = cmdargs.kas_override

    validate_notify_emails(cmdargs.notify_email)
    data["notify_emails"] = cmdargs.notify_email

    try:
        build = tuxsuite.Bitbake(data=data)
    except (AssertionError, tuxsuite.exceptions.TuxSuiteError) as e:
        error(e)
    print(
        "Building targets: {} with bitbake from {} source with distro: {} machine: {} arguments".format(
            build.build_definition.targets,
            build.build_definition.sources,
            build.build_definition.distro,
            build.build_definition.machine,
        )
    )
    try:
        build.build()
        print("uid: {}".format(build.uid))
    except tuxsuite.exceptions.BadRequest as e:
        error(str(e))

    build_result = True

    if cmdargs.no_wait:
        format_result(build.status, tuxapi_url=build.build_data)
    else:
        build_result = wait_for_object(build)

    if cmdargs.download:
        tuxsuite.download.download(build, cmdargs.output_dir)

    if cmdargs.json_out and build.status:
        with open(cmdargs.json_out, "w") as json_out:
            json_out.write(json.dumps(build.status, sort_keys=True, indent=4))
    if not build_result:
        sys.exit(1)


def handle_cancel(options, _, config):
    url = f"/v1/groups/{config.group}/projects/{config.project}/oebuilds/{options.uid}/cancel"
    ret = post(config, url, data={})
    print(f"canceling job for {options.uid}")

    if ret.status_code != 200:
        print(f"unable to cancel oebuild {options.uid}")
        raise tuxsuite.exceptions.URLNotFound()

    return 0


handlers = {
    "get": handle_get,
    "list": handle_list,
    "submit": handle_submit,
    "cancel": handle_cancel,
}


def bake_cmd_options(sp):
    sp.add_argument(
        "--json-out",
        help="Write json build status out to a named file path",
        type=pathlib.Path,
    )
    sp.add_argument(
        "-l",
        "--local-manifest",
        type=file_or_url,
        default=None,
        help=(
            "Path/URL to a local manifest file which will be used during repo sync."
            " This input is ignored if sources used is git_trees in the build"
            " definition. Should be a valid XML"
        ),
    )
    sp.add_argument(
        "-pm",
        "--pinned-manifest",
        type=file_or_url,
        default=None,
        help=(
            "Path/URL to a pinned manifest file which will be used during repo sync."
            " This input is ignored if sources used is git_trees in the build"
            " definition. Should be a valid XML"
        ),
    )
    sp.add_argument(
        "-k",
        "--kas-override",
        type=file_or_url,
        default=None,
        help=(
            "Path/URL to a kas config yml/yaml file which is appended to kas_yaml parameter."
            " This can be used to override the kas yaml file that is passed."
        ),
    )
    sp.add_argument(
        "-n",
        "--no-wait",
        default=False,
        action="store_true",
        help="Don't wait for the builds to finish",
    )
    sp.add_argument(
        "-d",
        "--download",
        default=False,
        action="store_true",
        help="Download artifacts after builds finish. Can't be used with no-wait",
    )
    sp.add_argument(
        "-o",
        "--output-dir",
        default=".",
        help="Directory where to download artifacts",
    )
    sp.add_argument(
        "-C",
        "--no-cache",
        default=False,
        action="store_true",
        help="Build without using any compilation cache",
    )
    sp.add_argument(
        "-P",
        "--private",
        action="store_false",
        help="Private build",
    )
    sp.add_argument(
        "--callback",
        default=None,
        help=(
            "Callback URL. The bake backend will send a POST request to "
            "this URL with signed data, when bake completes."
        ),
        type=is_url,
    )
    sp.add_argument(
        "--callback-header",
        help=(
            "Extra header to include in the POST request sent by the bake "
            "backend to the callback URL. The header string should be a key "
            "value pair separated by a ':' (colon). This option can be used "
            "multiple times to add multiple headers. "
            "Example: --callback-header 'X-First-Name: Joe'"
        ),
        type=str,
        action="append",
    )
    sp.add_argument(
        "-E",
        "--notify-email",
        help=(
            "Email address to be notified once the respective bake completes. "
            "This option can be used multiple times to add multiple "
            "notification email addresses."
        ),
        type=str,
        action="append",
    )


def setup_parser(parser):
    # "bake get"
    t = parser.add_parser("get")
    t.add_argument("uid")
    grp = t.add_mutually_exclusive_group()
    grp.add_argument(
        "--json", action="store_true", help="Output json bake build to stdout"
    )
    grp.add_argument(
        "--json-out",
        help="Write json bake build out to a named file path",
        type=argparse.FileType("w", encoding="utf-8"),
    )
    t.add_argument(
        "-l",
        "--list-artifacts",
        nargs="?",
        default=False,
        const=True,
        help="List the bake artifacts(files and directories) with maxdepth=1. Path (optional) can be passed "
        "to list the bake artifacts from specified path",
    )
    t.add_argument(
        "-d",
        "--download-artifacts",
        type=pathlib.Path,
        nargs="?",
        const=".",
        help="Download the bake artifacts(files only) with maxdepth=1. Path (optional) can be passed "
        "to download the bake artifacts at specified location. (default: current directory)",
    )

    # "bake list"
    t = parser.add_parser("list")
    t.add_argument(
        "--json", action="store_true", help="Output json bake list to stdout"
    )
    t.add_argument(
        "--json-out",
        help="Write json bake list out to a named file path",
        type=argparse.FileType("w", encoding="utf-8"),
    )
    t.add_argument("--limit", type=int, default=LIMIT)

    # "bake submit"
    t = parser.add_parser("submit")
    t.add_argument(
        "build_definition",
        metavar="build_definition",
        help="Path/URL to build_definition.yaml",
        nargs=1,
        type=file_or_url,
    )
    bake_cmd_options(t)

    # "bake cancel <uid>"
    t = parser.add_parser("cancel")
    t.add_argument("uid")

    return sorted(parser._name_parser_map.keys())
