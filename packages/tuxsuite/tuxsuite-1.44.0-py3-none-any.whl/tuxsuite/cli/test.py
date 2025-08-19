# -*- coding: utf-8 -*-

import argparse
import pathlib
import tuxsuite
import tuxsuite.exceptions
import tuxsuite.cli.colors as colors
import tuxsuite.cli.icons as icons
from tuxsuite.utils import error
from tuxsuite.cli.models import Test
from tuxsuite.cli.requests import apiurl, get, post, headers, get_storage
from tuxsuite.cli.utils import (
    LIMIT,
    datediff,
    fetch_next,
    key_value,
    wait_for_object,
    format_result,
    is_url,
    overlay_action,
    get_cb_headers,
    validate_notify_emails,
)
from tuxsuite.cli.yaml import yaml_load

import json
import requests
import sys
import time


COLORS = {
    "exception": "\033[1;31m",
    "error": "\033[1;31m",
    "warning": "\033[1;33m",
    "info": "\033[1;37m",
    "debug": "\033[0;37m",
    "target": "\033[32m",
    "input": "\033[0;35m",
    "feedback": "\033[0;33m",
    "results": "\033[1;34m",
    "dt": "\033[0;90m",
    "end": "\033[0m",
}


def handle_get(options, _, config):
    ret = get(
        config,
        f"/v1/groups/{config.group}/projects/{config.project}/tests/{options.uid}",
    )
    if ret.status_code != 200:
        raise NotImplementedError()

    test = Test.new(**ret.json())
    if options.json:
        print(test.as_json())
    elif options.json_out:
        options.json_out.write(json.dumps(test.as_dict(), indent=4))
    elif options.list_artifacts:
        path_url = (
            f"{test.download_url}{options.list_artifacts}/"
            if options.list_artifacts is not True
            else test.download_url
        )
        ret = get_storage(config, path_url).json()
        for folder in ret.get("folders", []):
            print(f"📁 {folder['Url'].split('/')[-2]}")
        for file in ret.get("files", []):
            print(f"📄 {file['Url'].split('/')[-1]}")
        if options.download_artifacts:
            tuxsuite.download.download_artifacts(
                config, test, options.download_artifacts, options.list_artifacts, ret
            )
    elif options.download_artifacts:
        tuxsuite.download.download_artifacts(config, test, options.download_artifacts)
    else:
        print(f"url     : {apiurl(config, test.url())}")
        print(f"project : {test.project}")
        print(f"uid     : {test.uid}")
        print(f"plan    : {test.plan}")
        if test.waiting_for:
            kind, waiting_for = test.waiting_for.split("#")
            print(f"{kind.lower()}   : {waiting_for}")
        print(f"user    : {test.user}")

        print(f"device  : {test.device}")
        print(f"kernel  : {test.kernel}")
        print(f"modules : {test.modules}")
        print(f"bootargs: {test.boot_args}")
        print(f"tests   : {', '.join(test.tests)}")
        print(f"overlays : {test.overlays}")

        if test.provisioning_time:
            print(f"{icons.PROVISIONING} time : {test.provisioning_time}")
        if test.running_time:
            print(f"{icons.RUNNING} time : {test.running_time}")

        if test.state == "finished":
            if test.result == "pass":
                icon = icons.PASS
            elif test.result == "error":
                icon = icons.ERROR
            elif test.result == "fail":
                icon = icons.FAIL
            elif test.result == "canceled":
                icon = icons.CANCELED
            elif test.result == "unknown":
                icon = icons.UNKNOWN
            print(f"{icon} time : {test.finished_time}")
        if test.duration:
            print(f"duration: {test.duration}")

        print(f"state   : {test.state}")
        color = ""
        if test.result == "pass":
            color = colors.green
        elif test.result in ["error", "fail"]:
            color = colors.red
        elif test.result == "canceled":
            color = colors.white
        elif test.result == "unknown":
            color = colors.purple
        print(f"result  : {color}{test.result}{colors.reset}")
    return 0


def handle_cancel(options, _, config):
    url = f"/v1/groups/{config.group}/projects/{config.project}/tests/{options.uid}/cancel"
    ret = post(config, url, data={})
    print(f"canceling job for {options.uid}")

    if ret.status_code != 200:
        print(f"unable to cancel test {options.uid}")
        raise tuxsuite.exceptions.URLNotFound()

    return 0


def handle_list(options, _, config):
    url = f"/v1/groups/{config.group}/projects/{config.project}/tests"
    ret = get(config, url)
    if ret.status_code != 200:
        raise NotImplementedError()

    tests = [Test.new(**t) for t in ret.json()["results"]]
    n_token = ret.json()["next"]
    if options.json or options.json_out:
        itrs = options.limit // LIMIT
        for _ in range(itrs):
            if not n_token:
                break
            items, n_token = fetch_next(Test, config, url, n_token)
            tests.extend(items)
        if options.json:
            print(json.dumps([t.as_dict() for t in tests[: options.limit]]))
        elif options.json_out:
            options.json_out.write(
                json.dumps([t.as_dict() for t in tests[: options.limit]], indent=4)
            )
    else:
        previous_pt = None
        while True:
            while len(tests) < options.limit and n_token:
                items, n_token = fetch_next(Test, config, url, n_token)
                tests.extend(items)

            if not tests:
                break

            for test in tests[: options.limit]:
                state = test.result if test.state == "finished" else test.state
                state_msg = (
                    (f"{colors.state(test.state, test.result)}{state}{colors.reset}")
                    if sys.stdout.isatty()
                    else state
                )
                all_tests = ",".join(test.tests)
                pt = test.provisioning_time
                if pt is None:
                    pt = "....-..-..T..:..:........."
                pt = pt[:-7]
                print(
                    f"{datediff(previous_pt, pt)} {test.uid} [{state_msg}] {all_tests}@{test.device} {test.kernel}"
                )

                previous_pt = pt
            tests = tests[options.limit :]
            if sys.stdout.isatty():
                try:
                    input(
                        "\nPress [ENTER] to see next list of tests, or Ctrl-C to quit:\n"
                    )
                except KeyboardInterrupt:
                    sys.exit(0)
    return 0


def handle_logs(options, _, config):
    ret = get(
        config,
        f"/v1/groups/{config.group}/projects/{config.project}/tests/{options.uid}",
    )
    if ret.status_code == 404:
        print(f"warning: {colors.red}Log unavailable{colors.reset}")
        return 0
    elif ret.status_code != 200:
        raise NotImplementedError()

    # TODO: add a wrapper around requests.get
    ret = requests.get(
        f"{ret.json()['download_url']}lava-logs.yaml", headers=headers(config)
    )
    if ret.status_code != 200:
        raise NotImplementedError()

    if options.raw:
        print(ret.text)
        return 0

    data = yaml_load(ret.text)
    for line in data:
        level = line["lvl"]
        msg = line["msg"]
        timestamp = line["dt"].split(".")[0]

        print(
            f"{COLORS['dt']}{timestamp}{COLORS['end']} {COLORS[level]}{msg}{COLORS['end']}"
        )
    return 0


def handle_results(options, _, config):
    ret = get(
        config,
        f"/v1/groups/{config.group}/projects/{config.project}/tests/{options.uid}",
    )
    if ret.status_code == 404:
        print(f"warning: {colors.red}Log unavailable{colors.reset}")
        return 0
    elif ret.status_code != 200:
        raise NotImplementedError()

    # TODO: add a wrapper around requests.get
    ret = requests.get(
        f"{ret.json()['download_url']}results.json", headers=headers(config)
    )

    if ret.status_code != 200:
        raise NotImplementedError()

    if options.raw:
        print(ret.text)
        return 0

    data = json.loads(ret.text)
    for k1, v1 in data.items():
        for k2, v2 in v1.items():
            for k3, v3 in v2.items():
                if v3 == "pass":
                    print(f"{k1}.{k2}: {colors.green}{v3}{colors.reset}")
                elif v3 == "fail":
                    print(f"{k1}.{k2}: {colors.red}{v3}{colors.reset}")
                elif v3 == "canceled":
                    print(f"{k1}.{k2}: {colors.white}{v3}{colors.reset}")
                elif v3 == "skip":
                    print(f"{k1}.{k2}: {colors.yellow}{v3}{colors.reset}")
                elif v3 == "unknown":
                    print(f"{k1}.{k2}: {colors.purple}{v3}{colors.reset}")
    return 0


def handle_wait(options, _, config):
    previous_state = None
    while True:
        ret = get(
            config,
            f"/v1/groups/{config.group}/projects/{config.project}/tests/{options.uid}",
        )
        if ret.status_code != 200:
            raise NotImplementedError()

        test = Test.new(**ret.json())
        if previous_state is None:
            previous_state = test.state
            print(f"url     : {apiurl(config, test.url())}")
            print(f"project : {test.project}")
            print(f"uid     : {test.uid}")
            print(f"plan    : {test.plan}")
            if test.waiting_for:
                kind, waiting_for = test.waiting_for.split("#")
                print(f"{kind.lower()}   : {waiting_for}")
            print(f"user    : {test.user}")

            print(f"device  : {test.device}")
            print(f"kernel  : {test.kernel}")
            print(f"modules : {test.modules}")
            print(f"bootargs: {test.boot_args}")
            print(f"tests   : {', '.join(test.tests)}")
            print(f"overlays : {test.overlays}")
            if test.provisioning_time:
                print(f"{icons.PROVISIONING} time : {test.provisioning_time}")
            if test.running_time:
                print(f"{icons.RUNNING} time : {test.running_time}")

        if test.state != previous_state:
            if test.state == "provisioning":
                print(f"{icons.PROVISIONING} time : {test.provisioning_time}")
            elif test.state == "running":
                print(f"{icons.RUNNING} time : {test.running_time}")
            previous_state = test.state
        if test.state == "finished":
            break
        time.sleep(5)

    if test.result == "pass":
        icon = icons.PASS
    elif test.result == "error":
        icon = icons.ERROR
    elif test.result == "fail":
        icon = icons.FAIL
    elif test.result == "canceled":
        icon = icons.CANCELED
    elif test.result == "unknown":
        icon = icons.UNKNOWN
    print(f"{icon} time : {test.finished_time}")

    if test.duration:
        print(f"duration: {test.duration}")

    print(f"state   : {test.state}")
    if test.result == "pass":
        color = colors.green
    elif test.result in ["error", "fail"]:
        color = colors.red
    elif test.result == "canceled":
        color = colors.white
    elif test.result == "unknown":
        color = colors.purple
    print(f"result  : {color}{test.result}{colors.reset}")
    return 0


def handle_submit(cmdargs, _, config):
    if not cmdargs.device:
        error("--device is a required argument")

    tests = [test for test in cmdargs.tests.split(",") if test]
    tests = [test for test in tests if test != "boot"]
    if cmdargs.wait_for:
        print(
            "Testing build {} on {} with {}".format(
                cmdargs.wait_for, cmdargs.device, ", ".join(["boot"] + tests)
            )
        )
        if cmdargs.kernel:
            error("--kernel and --wait-for are mutually exclusive")
        if cmdargs.modules:
            error("--modules and --wait-for are mutually exclusive")
    else:
        print(
            "Testing {} on {} with {}".format(
                cmdargs.kernel, cmdargs.device, ", ".join(["boot"] + tests)
            )
        )

    params = {}
    for p in cmdargs.parameters:
        params[p[0][0]] = p[0][1]

    timeouts_d = {}
    for t in cmdargs.timeouts:
        timeouts_d[t[0][0]] = int(t[0][1])

    cb_headers = None
    if cmdargs.callback_header:
        if not cmdargs.callback:
            error("--callback-header given without a --callback")
        else:
            cb_headers = get_cb_headers(cmdargs.callback_header)

    validate_notify_emails(cmdargs.notify_email)

    try:
        test = tuxsuite.Test(
            ap_romfw=cmdargs.ap_romfw,
            bios=cmdargs.bios,
            boot_args=cmdargs.boot_args,
            device=cmdargs.device,
            dtb=cmdargs.dtb,
            fip=cmdargs.fip,
            job_definition=cmdargs.job_definition,
            kernel=cmdargs.kernel,
            mcp_fw=cmdargs.mcp_fw,
            mcp_romfw=cmdargs.mcp_romfw,
            modules=cmdargs.modules,
            overlays=cmdargs.overlays,
            parameters=params,
            rootfs=cmdargs.rootfs,
            scp_fw=cmdargs.scp_fw,
            scp_romfw=cmdargs.scp_romfw,
            tests=tests,
            test_name=cmdargs.test_name,
            timeouts=timeouts_d,
            wait_for=cmdargs.wait_for,
            callback=cmdargs.callback,
            callback_headers=cb_headers,
            commands=cmdargs.commands,
            qemu_image=cmdargs.qemu_image,
            shared=cmdargs.shared,
            host=cmdargs.host,
            tuxbuild=cmdargs.tuxbuild,
            lab=cmdargs.lab,
            lava_test_plans_project=cmdargs.lava_test_plans_project,
            is_public=cmdargs.private,
            notify_emails=cmdargs.notify_email,
        )
    except (AssertionError, tuxsuite.exceptions.TuxSuiteError) as e:
        error(e)

    try:
        test.test()
        print("uid: {}".format(test.uid))
    except tuxsuite.exceptions.BadRequest as e:
        error(str(e))

    test_result = True

    if cmdargs.no_wait:
        format_result(test.status, test.url)
    else:
        test_result = wait_for_object(test)

    if cmdargs.json_out and test.status:
        with open(cmdargs.json_out, "w") as json_out:
            json_out.write(json.dumps(test.status, sort_keys=True, indent=4))

    # If the test did not pass, exit with exit code of 1
    if not test_result:
        sys.exit(1)


handlers = {
    "get": handle_get,
    "list": handle_list,
    "logs": handle_logs,
    "results": handle_results,
    "submit": handle_submit,
    "wait": handle_wait,
    "cancel": handle_cancel,
}


def test_cmd_options(sp):
    sp.add_argument(
        "--device",
        help="Device type",
        type=str,
    )
    sp.add_argument(
        "--kernel",
        help="URL of the kernel to test",
        default=None,
        type=str,
    )
    sp.add_argument(
        "--bios",
        help="URL of the bios to test",
        default=None,
        type=str,
    )
    sp.add_argument(
        "--dtb",
        help="URL of the dtb to test",
        default=None,
        type=str,
    )
    sp.add_argument(
        "--mcp-fw", help="URL of the MCP firmware to test", default=None, type=str
    )
    sp.add_argument(
        "--mcp-romfw",
        help="URL of the MCP ROM firmware to test",
        default=None,
        type=str,
    )
    sp.add_argument(
        "--modules",
        help="URL of the kernel modules",
        default=None,
        type=str,
    )
    sp.add_argument(
        "--rootfs",
        help="URL of the rootfs to test",
        default=None,
        type=str,
    )
    sp.add_argument(
        "--scp-fw", help="URL of the SCP firmware to test", default=None, type=str
    )
    sp.add_argument(
        "--ap-romfw",
        help="URL of the AP ROM firmware to test",
        default=None,
        type=str,
    )
    sp.add_argument(
        "--scp-romfw",
        help="URL of the SCP ROM firmware to test",
        default=None,
        type=str,
    )
    sp.add_argument("--fip", help="URL of the fip.bin to test", default=None, type=str)
    sp.add_argument(
        "--job-definition",
        help="URL/File of the lava job definition to test. Applicable to lava-fvp device type only",
        default=None,
        type=str,
    )
    sp.add_argument(
        "--overlay",
        default=[],
        metavar="URL/String",
        type=str,
        help=(
            "Tarball with overlay and optionally PATH to extract the tarball,"
            " default PATH '/'. Overlay can be specified multiple times"
        ),
        action=overlay_action,
        nargs="+",
        dest="overlays",
    )
    sp.add_argument(
        "--parameters",
        help="test parameters as KEY=VALUE",
        default=[],
        type=key_value,
        nargs="*",
        action="append",
    )
    sp.add_argument(
        "--tests",
        help="Comma separated list of tests",
        default="boot",
        type=str,
    )
    sp.add_argument(
        "--timeouts",
        help="timeouts as KEY=VALUE",
        default=[],
        type=key_value,
        nargs="*",
        action="append",
    )
    sp.add_argument(
        "--boot-args",
        help="Extra boot arguments",
        default=None,
        type=str,
    )
    sp.add_argument(
        "--wait-for",
        help="Wait for a test uid",
        default=None,
        type=str,
    )
    sp.add_argument(
        "-n",
        "--no-wait",
        default=False,
        action="store_true",
        help="Don't wait for tests to finish",
    )
    sp.add_argument(
        "--json-out",
        help="Write json test status out to a named file path",
        type=pathlib.Path,
    )
    sp.add_argument(
        "-P",
        "--private",
        default=True,
        action="store_false",
        help="Private Test",
    )
    sp.add_argument(
        "--callback",
        default=None,
        help=(
            "Callback URL. The test backend will send a POST request "
            "to this URL with signed data, when the test completes."
        ),
        type=is_url,
    )
    sp.add_argument(
        "--callback-header",
        help=(
            "Extra header to include in the POST request sent by the test "
            "backend to the callback URL. The header string should be a key "
            "value pair separated by a ':' (colon). This option can be used "
            "multiple times to add multiple headers. "
            "Example: --callback-header 'X-First-Name: Joe'"
        ),
        type=str,
        action="append",
    )
    sp.add_argument(
        "--commands",
        nargs="*",
        help="Space separated list of commands to run inside the VM",
        default=[],
    )
    sp.add_argument(
        "--qemu-image",
        default=None,
        help="Use qemu from the given container image",
    )
    sp.add_argument(
        "--shared",
        action="store_true",
        help="Publish artefacts stored by testcase in /mnt/tuxrun directory. Applies to qemu devices only.",
    )
    sp.add_argument(
        "--host",
        metavar="HOST",
        default="x86_64",
        help=(
            "Allow user to choose the host Runner. "
            "Default value is 'x86_64'. "
            "Valid values 'x86_64', 'm6a.large', 'm6id.large', 'm7g.large', 'm7gd.large'. "
            "x86_64 is 2vCPU + 4GB RAM with swap. "
            "m6a.large is 2vCPU + 8GB RAM with no swap. "
            "m7g.large is 2vCPU + 8GB RAM with no swap. "
            "m6id.large is 2vCPU + 8GB RAM with NVMe disk and no swap. "
            "m7gd.large is 2vCPU + 8GB RAM with NVMe disk and no swap. "
        ),
    )
    sp.add_argument(
        "--tuxbuild",
        metavar="URL",
        default=None,
        help="URL of a TuxBuild build",
        type=is_url,
    )
    sp.add_argument(
        "--lab",
        metavar="URL",
        default="https://lkft.validation.linaro.org",
        help="URL of LAVA lab instance",
        type=is_url,
    )
    sp.add_argument(
        "--lava-test-plans-project",
        default=None,
        help="Lava test plans project name",
        type=str,
    )
    sp.add_argument(
        "--test-name",
        help="User defined string to identify the test",
        type=str,
    )
    sp.add_argument(
        "-E",
        "--notify-email",
        help=(
            "Email address to be notified once the respective test completes. "
            "This option can be used multiple times to add multiple "
            "notification email addresses."
        ),
        type=str,
        action="append",
    )


def setup_parser(parser):
    # "test get <uid>"
    t = parser.add_parser("get")
    t.add_argument("uid")
    grp = t.add_mutually_exclusive_group()
    grp.add_argument("--json", action="store_true", help="Output json test to stdout")
    grp.add_argument(
        "--json-out",
        help="Write json test out to a named file path",
        type=argparse.FileType("w", encoding="utf-8"),
    )
    t.add_argument(
        "-l",
        "--list-artifacts",
        nargs="?",
        default=False,
        const=True,
        help="List the test artifacts(files and directories) with maxdepth=1. Path (optional) can be passed "
        "to list the test artifacts from specified path",
    )
    t.add_argument(
        "-d",
        "--download-artifacts",
        type=pathlib.Path,
        nargs="?",
        const=".",
        help="Download the test artifacts(files only) with maxdepth=1. Path (optional) can be passed "
        "to download the test artifacts at specified location. (default: current directory)",
    )

    # "test list"
    t = parser.add_parser("list")
    t.add_argument(
        "--json", action="store_true", help="Output json test list to stdout"
    )
    t.add_argument(
        "--json-out",
        help="Write json test list out to a named file path",
        type=argparse.FileType("w", encoding="utf-8"),
    )
    t.add_argument("--limit", type=int, default=LIMIT)

    # "test logs <uid>"
    t = parser.add_parser("logs")
    t.add_argument("uid")
    t.add_argument("--raw", action="store_true")

    # "test results <uid>"
    t = parser.add_parser("results")
    t.add_argument("uid")
    t.add_argument("--raw", action="store_true")

    # "test submit"
    t = parser.add_parser("submit")
    test_cmd_options(t)

    # "test wait <uid>"
    t = parser.add_parser("wait")
    t.add_argument("uid")

    # "test cancel <uid>"
    t = parser.add_parser("cancel")
    t.add_argument("uid")

    return sorted(parser._name_parser_map.keys())
