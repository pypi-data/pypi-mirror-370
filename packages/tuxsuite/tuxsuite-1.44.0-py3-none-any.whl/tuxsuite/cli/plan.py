# -*- coding: utf-8 -*-

from itertools import chain
from copy import deepcopy
from pathlib import Path

import tuxsuite
from tuxsuite.local_plan import LocalPlan
import tuxsuite.cli.colors as colors
import tuxsuite.cli.icons as icons
from tuxsuite.utils import error
from tuxsuite.cli.models import Plan
from tuxsuite.cli.requests import get, post
from tuxsuite.cli.common import common_options
from tuxsuite.cli.yaml import yaml_dump, yaml_load
from tuxsuite.cli.utils import (
    LIMIT,
    datediff,
    fetch_next,
    file_or_url,
    format_result,
    format_plan_result,
    key_value,
    show_log,
    wait_for_object,
    is_url,
    get_cb_headers,
    load_plan,
    validate_notify_emails,
)

import argparse
import json
import sys


def format_plan(build, tests, sanity_test=None):
    if build.result == "pass":
        if build.warnings_count == 0:
            icon = icons.PASS
            message = "Pass"
            color = colors.green
        else:
            icon = icons.WARNING
            color = colors.yellow
            if build.warnings_count == 1:
                message = "Pass (1 warning)"
            else:
                message = "Pass ({} warnings)".format(build.warnings_count)
    elif build.result == "fail":
        icon = icons.FAIL
        color = colors.red
        if build.errors_count == 1:
            message = "Fail (1 error)"
        else:
            message = "Fail ({} errors)".format(build.errors_count)
    elif build.result == "error":
        icon = icons.ERROR
        color = colors.red
        message = build.status_message
    elif build.result == "canceled":
        icon = icons.CANCELED
        color = colors.white
        message = build.status_message
    elif build.result == "unknown":
        icon = icons.UNKNOWN
        color = colors.purple
        message = "Result unknown"
    else:
        raise NotImplementedError()

    builds = build.get_builds_message(icon, color, message)

    tests_str = f" Sanity: {format_test(sanity_test)}" if sanity_test else ""
    tests_pass = sorted(
        set(chain.from_iterable([t.tests for t in tests if t.result == "pass"]))
    )
    tests_fail = sorted(
        set(chain.from_iterable([t.tests for t in tests if t.result == "fail"]))
    )
    tests_error = sorted(
        set(chain.from_iterable([t.tests for t in tests if t.result == "error"]))
    )
    tests_unknown = sorted(
        set(chain.from_iterable([t.tests for t in tests if t.result == "unknown"]))
    )
    tests_canceled = sorted(
        set(chain.from_iterable([t.tests for t in tests if t.result == "canceled"]))
    )
    if tests_pass:
        tests_str += (
            f" {icons.PASS} {colors.green}Pass: {','.join(tests_pass)}{colors.reset}"
        )
    if tests_fail:
        tests_str += (
            f" {icons.FAIL} {colors.red}Fail: {','.join(tests_fail)}{colors.reset}"
        )
    if tests_error:
        tests_str += (
            f" {icons.ERROR} {colors.red}Error: {','.join(tests_error)}{colors.reset}"
        )
    if tests_unknown:
        tests_str += f" {icons.UNKNOWN} {colors.purple}Unknown: {','.join(tests_unknown)}{colors.reset}"
    if tests_canceled:
        tests_str += f" {icons.CANCELED} {colors.white}Canceled: {','.join(tests_canceled)}{colors.reset}"

    return builds + tests_str


def format_test(test):
    if test.result == "pass":
        icon = icons.PASS
        color = colors.green
        message = "Pass"
    elif test.result == "fail":
        icon = icons.FAIL
        color = colors.red
        message = "Fail"
    elif test.result == "unknown":
        icon = icons.UNKNOWN
        color = colors.purple
        message = "Unknown"
    elif test.result == "canceled":
        icon = icons.CANCELED
        color = colors.white
        message = "Canceled"
    elif test.result == "error":
        icon = icons.ERROR
        color = colors.red
        message = "Error"
    else:
        raise NotImplementedError()

    return (
        test.uid
        + " "
        + f"test {icon} {color}{message}: {','.join(test.tests)}{colors.reset}"
    )


def handle_get(options, _, config):
    params = {}
    if options.result:
        params["result"] = options.result
    ret = get(
        config,
        f"/v1/groups/{config.group}/projects/{config.project}/plans/{options.uid}",
        params,
    )
    if ret.status_code == 404:
        err_msg = (
            f"\t{ret.json().get('error')}\n"
            "\tCheck if the plan's group/project are correct."
        )
        error(err_msg)

    if ret.status_code != 200:
        raise NotImplementedError()

    data = ret.json()

    start_builds = data["builds"]["next"]
    start_tests = data["tests"]["next"]
    start_oebuilds = data["oebuilds"]["next"]
    while start_builds or start_tests or start_oebuilds:
        ret = get(
            config,
            f"/v1/groups/{config.group}/projects/{config.project}/plans/{options.uid}",
            params={
                "start_builds": start_builds,
                "start_tests": start_tests,
                "start_oebuilds": start_oebuilds,
            },
        )
        if ret.status_code != 200:
            raise NotImplementedError()

        datan = ret.json()
        if start_builds:
            data["builds"]["results"].extend(datan["builds"]["results"])
            start_builds = datan["builds"]["next"]
        if start_tests:
            data["tests"]["results"].extend(datan["tests"]["results"])
            start_tests = datan["tests"]["next"]
        if start_oebuilds:
            data["oebuilds"]["results"].extend(datan["oebuilds"]["results"])
            start_oebuilds = datan["oebuilds"]["next"]

    plan = Plan.new(**data)
    if options.json:
        print(plan.as_json())
    elif options.json_out:
        out = {}
        for kind in ["builds", "oebuilds", "tests"]:
            if data[kind]["results"]:
                out[kind] = {}
                for item in data[kind]["results"]:
                    out[kind][item["uid"]] = item
        options.json_out.write(json.dumps(out, indent=4, sort_keys=True))
    else:
        print(
            f"{plan.provisioning_time[:-7]} {plan.uid} {plan.name} ({plan.description})"
        )

        for build in chain(
            plan.passing(),
            plan.warning(),
            plan.failing(),
            plan.errors(),
            plan.canceled(),
            plan.unknown(),
        ):
            tests, sanity_test = plan._tests_wait_for(build.uid, get_sanity=True)
            print(format_plan(build, tests, sanity_test))
        # Print stand alone tests or sanity dependent tests
        for test in [t for t in plan.tests if t.waiting_for is None]:
            dependent_tests = plan._dependent_tests(test.uid)
            if dependent_tests:
                for dt in dependent_tests:
                    print(f"Sanity: {format_test(test)} {format_test(dt)}")
            else:
                print(format_test(test))

        bs = f"builds ({len(plan.all_builds)}):"
        provisioning = len(plan.filter_builds(lambda _, b: b.state == "provisioning"))
        running = len(plan.filter_builds(lambda _, b: b.state == "running"))
        passing = len(
            plan.filter_builds(
                lambda _, b: b.result == "pass" and b.warnings_count == 0
            )
        )
        warning = len(
            plan.filter_builds(
                lambda _, b: b.result == "pass" and b.warnings_count != 0
            )
        )
        failing = len(plan.filter_builds(lambda _, b: b.result == "fail"))
        err = len(plan.filter_builds(lambda _, b: b.result == "error"))
        canceled = len(plan.filter_builds(lambda _, b: b.result == "canceled"))
        unknown = len(plan.filter_builds(lambda _, b: b.result == "unknown"))

        if provisioning:
            bs += f" {icons.PROVISIONING} {provisioning}"
        if running:
            bs += f" {icons.RUNNING} {running}"
        if passing:
            bs += f" {icons.PASS} {passing}"
        if warning:
            bs += f" {icons.WARNING} {warning}"
        if failing:
            bs += f" {icons.FAIL} {failing}"
        if err:
            bs += f" {icons.ERROR} {err}"
        if canceled:
            bs += f" {icons.CANCELED} {canceled}"
        if unknown:
            bs += f" {icons.UNKNOWN} {unknown}"

        print(bs)

        ts = f"tests ({len(plan.tests)}):"
        waiting = len(plan.filter_tests(lambda _, t: t.state == "waiting"))
        provisioning = len(plan.filter_tests(lambda _, t: t.state == "provisioning"))
        running = len(plan.filter_tests(lambda _, t: t.state == "running"))
        passing = len(plan.filter_tests(lambda _, t: t.result == "pass"))
        failing = len(plan.filter_tests(lambda _, t: t.result == "fail"))
        err = len(plan.filter_tests(lambda _, t: t.result == "error"))
        canceled = len(plan.filter_tests(lambda _, t: t.result == "canceled"))
        unknown = len(plan.filter_tests(lambda _, t: t.result == "unknown"))

        if waiting:
            ts += f" {icons.WAITING} {waiting}"
        if provisioning:
            ts += f" {icons.PROVISIONING} {provisioning}"
        if running:
            ts += f" {icons.RUNNING} {running}"
        if passing:
            ts += f" {icons.PASS} {passing}"
        if failing:
            ts += f" {icons.FAIL} {failing}"
        if err:
            ts += f" {icons.ERROR} {err}"
        if canceled:
            ts += f" {icons.CANCELED} {canceled}"
        if unknown:
            ts += f" {icons.UNKNOWN} {unknown}"
        print(ts)
    return 0


def handle_cancel(options, _, config):
    ret = get(
        config,
        f"/v1/groups/{config.group}/projects/{config.project}/plans/{options.uid}",
    )
    if ret.status_code == 404:
        err_msg = (
            f"\t{ret.json().get('error')}\n"
            "\tCheck if the plan UID or group/project are correct."
        )
        error(err_msg)
    url = f"/v1/groups/{config.group}/projects/{config.project}/plans/{options.uid}/cancel"
    ret = post(config, url, data={})
    print(f"canceling plan {options.uid}")

    if ret.status_code != 200:
        print("plan not canceled")
        raise tuxsuite.exceptions.URLNotFound()

    return 0


def handle_wait(options, _, config):
    ret = get(
        config,
        f"/v1/groups/{config.group}/projects/{config.project}/plans/{options.uid}",
    )
    if ret.status_code != 200:
        raise NotImplementedError()

    data = ret.json()
    start_builds = data["builds"]["next"]
    start_tests = data["tests"]["next"]
    start_oebuilds = data["oebuilds"]["next"]
    while start_builds or start_tests or start_oebuilds:
        ret = get(
            config,
            f"/v1/groups/{config.group}/projects/{config.project}/plans/{options.uid}",
            params={
                "start_builds": start_builds,
                "start_tests": start_tests,
                "start_oebuilds": start_oebuilds,
            },
        )
        if ret.status_code != 200:
            raise NotImplementedError()
        datan = ret.json()
        if start_builds:
            data["builds"]["results"].extend(datan["builds"]["results"])
            start_builds = datan["builds"]["next"]
        if start_tests:
            data["tests"]["results"].extend(datan["tests"]["results"])
            start_tests = datan["tests"]["next"]
        if start_oebuilds:
            data["oebuilds"]["results"].extend(datan["oebuilds"]["results"])
            start_oebuilds = datan["oebuilds"]["next"]

    data["project"] = config.project
    plan = tuxsuite.Plan(config, **data)
    plan.plan = data["uid"]
    plan.load(plan.get_plan())
    if plan.builds:
        for build in plan.builds:
            build.build_data = f"{plan.url}/builds/{build.uid}"

    wait_for_object(plan)

    for b in chain(
        plan.passing(),
        plan.warning(),
        plan.failing(),
        plan.errors(),
        plan.canceled(),
        plan.unknown(),
    ):
        format_plan_result(b, plan._tests_wait_for(b.uid))
    return 0


def handle_list(options, _, config):
    url = f"/v1/groups/{config.group}/projects/{config.project}/plans"
    ret = get(config, url)
    if ret.status_code != 200:
        raise NotImplementedError()

    plans = [Plan.new(**p) for p in ret.json()["results"]]
    n_token = ret.json()["next"]
    if options.json or options.json_out:
        itrs = options.limit // LIMIT
        for _ in range(itrs):
            if not n_token:
                break
            items, n_token = fetch_next(Plan, config, url, n_token)
            plans.extend(items)
        if options.json:
            print(json.dumps([p.as_dict() for p in plans[: options.limit]]))
        elif options.json_out:
            options.json_out.write(
                json.dumps([p.as_dict() for p in plans[: options.limit]], indent=4)
            )
    else:
        previous_pt = None
        while True:
            while len(plans) < options.limit and n_token:
                items, n_token = fetch_next(Plan, config, url, n_token)
                plans.extend(items)

            if not plans:
                break

            for plan in plans[: options.limit]:
                pt = plan.provisioning_time
                if pt is None:
                    pt = "....-..-..T..:..:........."
                pt = pt[:-7]

                print(
                    f"{datediff(previous_pt, pt)} {plan.uid} {plan.name} ({plan.description})"
                )
                previous_pt = pt
            plans = plans[options.limit :]
            if sys.stdout.isatty():
                try:
                    input(
                        "\nPress [ENTER] to see next list of plans, or Ctrl-C to quit:\n"
                    )
                except KeyboardInterrupt:
                    sys.exit(0)

    return 0


def handle_submit(cmdargs, extra_arguments, config):
    if cmdargs.local_manifest and cmdargs.pinned_manifest:
        error("Either local manifest or pinned manifest to be provided, not both")

    if extra_arguments:
        error(f"Unknown option: {extra_arguments}")
        sys.exit(2)

    if cmdargs.git_head:
        try:
            cmdargs.git_repo, cmdargs.git_sha = tuxsuite.gitutils.get_git_head()
        except Exception as e:
            error(e)

    cb_headers = None
    if cmdargs.callback_header:
        if not cmdargs.callback:
            error("--callback-header given without a --callback")
        else:
            cb_headers = get_cb_headers(cmdargs.callback_header)

    pc_headers = None
    if cmdargs.plan_callback_header:
        if not cmdargs.plan_callback:
            error("--plan-callback-header given without a --plan-callback")
        else:
            pc_headers = get_cb_headers(cmdargs.plan_callback_header)

    validate_notify_emails(cmdargs.notify_email)

    try:
        plan_config = tuxsuite.config.PlanConfig(
            cmdargs.name, cmdargs.description, cmdargs.config[0], cmdargs.job_name
        )

        # setting respective plan type class obj (Kernel or Bake)
        plan_type = plan_config.plan_type

        if plan_config.schema_warning:
            error(f"Invalid plan file: {plan_config.schema_warning}")

        if not plan_config.plan:
            error("Empty plan, skipping")
            return
        plan = tuxsuite.Plan(
            plan_config,
            git_repo=cmdargs.git_repo,
            git_sha=cmdargs.git_sha,
            git_ref=cmdargs.git_ref,
            patch_series=cmdargs.patch_series,
            parameters=cmdargs.parameters,
            no_cache=cmdargs.no_cache,
            manifest_file=cmdargs.local_manifest,
            pinned_manifest=cmdargs.pinned_manifest,
            is_public=cmdargs.private,
            kas_override=cmdargs.kas_override,
            lab=cmdargs.lab,
            lava_test_plans_project=cmdargs.lava_test_plans_project,
            callback=cmdargs.callback,
            callback_headers=cb_headers,
            plan_callback=cmdargs.plan_callback,
            plan_callback_headers=pc_headers,
            notify_emails=cmdargs.notify_email,
        )
    except (AssertionError, tuxsuite.exceptions.TuxSuiteError) as e:
        error(e)

    plan_type.plan_info(plan_config.name, plan_config.description)

    try:
        plan.submit()
        print("Plan {}/plans/{}\n".format(plan.url, plan.plan))
        print("uid: {}".format(plan.plan))
    except tuxsuite.exceptions.BadRequest as e:
        error(str(e))

    result = True

    if cmdargs.no_wait:
        for build in plan.builds:
            format_result(build.status, build.build_data)
        for test in plan.tests:
            format_result(test.status, plan.url + "/tests/{}".format(test.uid))
    else:
        result = wait_for_object(plan)
        print(f"\nSummary: {plan.url}/plans/{plan.plan}")
        for b in chain(
            plan.passing(),
            plan.warning(),
            plan.failing(),
            plan.errors(),
            plan.canceled(),
            plan.unknown(),
        ):
            format_plan_result(b, plan._tests_wait_for(b.uid))

    if cmdargs.json_out and plan.status:
        with open(cmdargs.json_out, "w") as json_out:
            json_out.write(json.dumps(plan.status, sort_keys=True, indent=4))
    if cmdargs.download:
        for build in plan.builds:
            tuxsuite.download.download(build, cmdargs.output_dir)
    if cmdargs.show_logs:
        for build in plan.builds:
            show_log(build, cmdargs.download, cmdargs.output_dir)

    if not result:
        sys.exit(1)


def handle_create(cmdargs, extra_arguments):
    if not (cmdargs.test_plan or cmdargs.build_plan):
        error("At least one of '--build-plan' or '--test-plan' is required")
    if not cmdargs.build_plan and (
        cmdargs.overwrite_targets or cmdargs.append_kconfigs
    ):
        error(
            "'--build-plan' is necessary if '--overwrite-target' or '--append-kconfig' is provided"
        )

    if extra_arguments:
        error(f"Unknown option: {extra_arguments}")
    tux_plan = {}
    # test params have to be updated as per lkft plan parameters
    test_params = {"KSELFTEST": "$BUILD/kselftest.tar.xz", "PERF": "$BUILD/perf.tar.xz"}
    if cmdargs.build_plan:
        build_jobs = load_plan(cmdargs.build_plan)["jobs"]
        if len(build_jobs) == 1 and all(
            key in ["name", "build"] for key in build_jobs[0]
        ):
            # single build job
            build_job = build_jobs[0]["build"]
            # overwrite targets
            if cmdargs.overwrite_targets:
                build_job["targets"] = cmdargs.overwrite_targets
            # update kconfig
            kconfig = build_job.get("kconfig", []) or []
            build_job["kconfig"] = kconfig
            if isinstance(kconfig, str):
                build_job["kconfig"] = [kconfig] + cmdargs.append_kconfigs
            elif isinstance(kconfig, list):
                build_job["kconfig"].extend(cmdargs.append_kconfigs)
            tux_plan["build"] = deepcopy(build_job)
        else:
            error(
                "The build plan file is invalid. It should only include one build job"
            )
    if cmdargs.test_plan:
        test_jobs = load_plan(cmdargs.test_plan)["jobs"]
        if len(test_jobs) == 1 and all(key in ["name", "test"] for key in test_jobs[0]):
            # single test job
            test_job = test_jobs[0]["test"]
            if cmdargs.build_plan:
                test_job["kernel"] = None
                test_job["modules"] = None
                # process parameters
                for key, val in test_job.get("parameters", {}).items():
                    test_job["parameters"][key] = test_params.get(key, val)
                # process dtb
                dtb = test_job.get("dtb")
                test_job["dtb"] = dtb.rsplit("dtbs/")[-1] if dtb else None

            tux_plan["tests"] = [
                deepcopy(test_job) for _ in range(cmdargs.test_retrigger)
            ]
        else:
            error("The test plan file is invalid. It should only include one test job")

    final_plan = """
version: 1
name: Tux Plan
description: Generated plan from tuxsuite cli
jobs:
- name: Tux Plan
"""
    # process plan
    final_plan = yaml_load(final_plan, True)
    final_plan["jobs"][0].update(tux_plan)

    if cmdargs.output_plan:
        with open(cmdargs.output_plan.name, "w") as f:
            yaml_dump(final_plan, f, sort_keys=False)
    else:
        print(yaml_dump(final_plan, sort_keys=False))

    return 0


def handle_execute(cmdargs, extra_arguments):
    if extra_arguments:
        error(f"Unknown option: {extra_arguments}")

    try:
        plan_cfg = tuxsuite.config.PlanConfig(
            "Local plan", "Local plan", cmdargs.config[0], cmdargs.job_name
        )

        if not isinstance(plan_cfg.plan_type, tuxsuite.BuildPlan):
            error("Unsupported plan type")

        if plan_cfg.schema_warning:
            error(f"Invalid plan file: {plan_cfg.schema_warning}")

        LocalPlan.check_tools(cmdargs.runtime)
        plan = LocalPlan(cmdargs, plan_cfg)
        plan.submit()
        plan.summary()
    except (TypeError, tuxsuite.exceptions.TuxSuiteError) as e:
        error(e)

    return plan.ret_code


handlers = {
    "get": handle_get,
    "list": handle_list,
    "wait": handle_wait,
    "submit": handle_submit,
    "cancel": handle_cancel,
    "create": handle_create,
    "execute": handle_execute,
}


def plan_cmd_options(sp):
    sp.add_argument("--name", help="Set name")
    sp.add_argument("--description", help="Set description")
    sp.add_argument(
        "--job-name", action="append", help="Job name (may be specified multiple times)"
    )
    sp.add_argument(
        "--limit",
        default=LIMIT,
        help="Limit to LIMIT output. Used with [list]",
    )
    sp.add_argument(
        "--json",
        default=False,
        action="store_true",
        help="Show json output. Used with [get | list]",
    )
    sp.add_argument(
        "-l",
        "--local-manifest",
        default=None,
        help=(
            "Path to a local manifest file which will be used during repo sync. "
            "This input is ignored if sources used is git_trees in the build "
            "definition. Should be a valid XML. This option is only applicable in case of bake plan."
        ),
        type=file_or_url,
    )
    sp.add_argument(
        "-pm",
        "--pinned-manifest",
        default=None,
        help=(
            "Path to a pinned manifest file which will be used during repo sync. "
            "This input is ignored if sources used is git_trees in the build "
            "definition. Should be a valid XML. This option is only applicable in case of bake plan."
        ),
        type=file_or_url,
    )
    sp.add_argument(
        "-k",
        "--kas-override",
        type=file_or_url,
        default=None,
        help=(
            "Path to a kas config yml/yaml file which is appended to kas_yaml parameter."
            " This can be used to override the kas yaml file that is passed."
        ),
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
        "--parameters",
        help="test parameters as KEY=VALUE. This option can be used multiple times to add multiple parameters",
        default=[],
        type=key_value,
        action="append",
    )


def plan_create_options(sp):
    sp.add_argument(
        "--build-plan",
        default=None,
        help="Path/URL to a build plan file",
        type=file_or_url,
    )
    sp.add_argument(
        "--test-plan",
        default=None,
        help="Path/URL to a test plan file",
        type=file_or_url,
    )
    sp.add_argument(
        "--test-retrigger",
        help="Number of times the test should be triggered",
        default=1,
        type=int,
    )
    sp.add_argument(
        "--overwrite-target",
        default=[],
        help="Targets to overwrite to build plan targets. Can be specified multiple times",
        type=str,
        action="append",
        dest="overwrite_targets",
    )
    sp.add_argument(
        "--append-kconfig",
        help="Kconfig to append to build plan Kconfigs. Can be specified multiple times",
        default=[],
        type=str,
        action="append",
        dest="append_kconfigs",
    )
    sp.add_argument(
        "--output-plan",
        help="Write created plan out to a named file path",
        type=argparse.FileType("w", encoding="utf-8"),
    )


def plan_execute_options(sp):
    sp.add_argument(
        "--tree",
        type=Path,
        default=".",
        help="Path to Linux kernel source (default: .).",
    )
    sp.add_argument(
        "-r",
        "--runtime",
        default="podman",
        choices=["docker", "podman"],
    )
    sp.add_argument(
        "--job-name",
        action="append",
        help="Job name (may be specified multiple times).",
    )
    sp.add_argument(
        "-d",
        "--output-dir",
        type=Path,
        help="Output dir to save build or test artifacts (default: ~/.cache/tuxsuite/plan/)",
    )
    sp.add_argument(
        "-w",
        "--wrapper",
        type=str,
        default="none",
        choices=["ccache", "sccache", "none"],
        help=(
            "Compiler wrapper to use in the build. Default: none. Supported: %(choices)s. "
            "When used with containers, either the wrapper binary must be available in the "
            "container image, OR you can pass --wrapper=/path/to/WRAPPER and WRAPPER will be "
            "bind mounted in /usr/local/bin inside the container (for this to work WRAPPER needs "
            "to be a static binary, or have its shared library dependencies available inside the container)."
        ),
    )


def setup_parser(parser):
    # "plan get <uid>"
    p = parser.add_parser("get")
    p.add_argument("uid")
    p.add_argument("--json", action="store_true", help="Output json plan to stdout")
    p.add_argument(
        "--json-out",
        help="Write json plan out to a named file path",
        type=argparse.FileType("w", encoding="utf-8"),
    )
    p.add_argument(
        "--result",
        help="Filter for a particular result (pass|fail); omit to pull all results.",
        choices=("pass", "fail"),
    )

    # "plan list"
    p = parser.add_parser("list")
    p.add_argument(
        "--json", action="store_true", help="Output json plan list to stdout"
    )
    p.add_argument(
        "--json-out",
        help="Write json plan list out to a named file path",
        type=argparse.FileType("w", encoding="utf-8"),
    )
    p.add_argument("--limit", type=int, default=LIMIT)

    # "plan"
    t = parser.add_parser("submit")
    t.add_argument(
        "config",
        metavar="config",
        nargs=1,
        help="Plan config",
        const=None,
    )
    plan_cmd_options(t)
    common_options(t)
    t.add_argument(
        "--plan-callback",
        default=None,
        help=(
            "Plan callback URL. Plan will send a POST request to this URL "
            "with signed data, when the plan completes."
        ),
        type=is_url,
    )
    t.add_argument(
        "--plan-callback-header",
        help=(
            "Extra header to include in the POST request sent to the plan "
            "callback URL. The header string should be a key value pair "
            "separated by a ':' (colon). This option can be used multiple "
            "times to add multiple headers. Example: --plan-callback-header "
            '"X-First-Name: Joe"'
        ),
        type=str,
        action="append",
    )

    # plan wait <uid>
    t = parser.add_parser("wait")
    t.add_argument("uid")

    # plan cancel <uid>
    t = parser.add_parser("cancel")
    t.add_argument("uid")

    # plan create
    t = parser.add_parser("create")
    plan_create_options(t)

    # plan execute
    t = parser.add_parser("execute", description="Run a plan file locally")
    t.add_argument(
        "config",
        metavar="config",
        nargs=1,
        help="Plan config",
        const=None,
    )
    plan_execute_options(t)

    return sorted(parser._name_parser_map.keys())
