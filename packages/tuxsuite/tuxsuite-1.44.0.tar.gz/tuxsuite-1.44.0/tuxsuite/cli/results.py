# -*- coding: utf-8 -*-

import json
import argparse
import tuxsuite

from itertools import chain
from tuxsuite.utils import error
from tuxsuite.cli.utils import (
    format_result,
    format_plan_result,
)


def plan_summary(plan):
    bs = f"builds ({len(plan.builds)}):"
    provisioning = len(
        plan.filter_builds(lambda _, b: b.status["state"] == "provisioning")
    )
    running = len(plan.filter_builds(lambda _, b: b.status["state"] == "running"))
    passing = len(
        plan.filter_builds(
            lambda _, b: b.status["result"] == "pass"
            and b.status["warnings_count"] == 0
        )
    )
    warning = len(
        plan.filter_builds(
            lambda _, b: b.status["result"] == "pass"
            and b.status["warnings_count"] != 0
        )
    )
    failing = len(plan.filter_builds(lambda _, b: b.status["result"] == "fail"))
    error = len(plan.filter_builds(lambda _, b: b.status["result"] == "error"))
    canceled = len(plan.filter_builds(lambda _, b: b.status["result"] == "canceled"))
    unknown = len(plan.filter_builds(lambda _, b: b.status["result"] == "unknown"))

    if provisioning:
        bs += f" ⚙️  {provisioning}"
    if running:
        bs += f" 🚀 {running}"
    if passing:
        bs += f" 🎉 {passing}"
    if warning:
        bs += f" 👾 {warning}"
    if failing:
        bs += f" 👹 {failing}"
    if error:
        bs += f" 🔧 {error}"
    if canceled:
        bs += f" ⚠️  {canceled}"
    if unknown:
        bs += f" 🧐 {unknown}"

    ts = f"tests ({len(plan.tests)}):"
    waiting = len(plan.filter_tests(lambda _, t: t.status["state"] == "waiting"))
    provisioning = len(
        plan.filter_tests(lambda _, t: t.status["state"] == "provisioning")
    )
    running = len(plan.filter_tests(lambda _, t: t.status["state"] == "running"))
    passing = len(plan.filter_tests(lambda _, t: t.status["result"] == "pass"))
    failing = len(plan.filter_tests(lambda _, t: t.status["result"] == "fail"))
    error = len(plan.filter_tests(lambda _, t: t.status["result"] == "error"))
    canceled = len(plan.filter_tests(lambda _, t: t.status["result"] == "canceled"))
    unknown = len(plan.filter_tests(lambda _, t: t.status["result"] == "unknown"))

    if waiting:
        ts += f" ⏳ {waiting}"
    if provisioning:
        ts += f" ⚙️  {provisioning}"
    if running:
        ts += f" 🚀 {running}"
    if passing:
        ts += f" 🎉 {passing}"
    if failing:
        ts += f" 👹 {failing}"
    if error:
        ts += f" 🔧 {error}"
    if canceled:
        ts += f" ⚠️  {canceled}"
    if unknown:
        ts += f" 🧐 {unknown}"
    return (bs, ts)


def handle_fetch(cmdargs, _, config):
    build = cmdargs.build
    test = cmdargs.test
    plan = cmdargs.plan
    oebuild = cmdargs.oebuild
    result_json = {}

    try:
        results = tuxsuite.Results()
    except (AssertionError, tuxsuite.exceptions.TuxSuiteError) as e:
        error(e)

    try:
        if cmdargs.from_json:
            data = json.loads(cmdargs.from_json.read())
            if "builds" in data and "tests" in data:
                plan = data["builds"][list(data["builds"].keys())[0]]["plan"]
            elif "build_name" in data:
                build = data["uid"]
            elif "tests" in data:
                test = data["uid"]
            elif "sources" in data:
                oebuild = data["uid"]
            elif isinstance(data, list):
                # Now can able to parse and fetch results of build/tests/oebuilds from json file
                # TODO - list of plans not included yet
                result_json_map = {}
                result_list = []
                result_json, tuxapi_url = results.get_all()
                result_json.pop("plans", None)
                # prepare map of results based on their ksuids
                for key in result_json.keys():
                    for result in result_json[key].get("results", None):
                        result_json_map[result["uid"]] = {
                            **result,
                            **{"tuxapi_url": f"{tuxapi_url}/{key}/{result['uid']}"},
                        }

                for res in data:
                    if result_json_map.get(res["uid"], None):
                        result, tuxapi_url = (
                            result_json_map[res["uid"]],
                            result_json_map[res["uid"]]["tuxapi_url"],
                        )
                        format_result(result, tuxapi_url)
                        if cmdargs.json_out:
                            result_list.append(result)
                result_json = result_list

        elif not any([build, test, plan, oebuild]):  # get all results with no options
            result_json, tuxapi_url = results.get_all()
            for key in result_json.keys():
                print(f"{key.capitalize()}:")
                for result in result_json[key].get("results", None):
                    if key == "plans":
                        print(f"{result['uid']}: {result['name']} {result['project']}")
                    else:
                        format_result(result, f"{tuxapi_url}/{key}/{result['uid']}")
                print("\n")

        if build:
            results.uid = build
            result_json, tuxapi_build_url = results.get_build()
            format_result(result_json, tuxapi_build_url)
        if test:
            results.uid = test
            result_json, tuxapi_tests_url = results.get_test()
            format_result(result_json, tuxapi_tests_url)
        if plan:
            results.uid = plan
            result_json, tuxapi_plan_url = results.get_plan()
            plan_obj = tuxsuite.Plan("")
            plan_obj.plan = plan
            plan_obj.load(result_json)
            print(f"Summary: {plan_obj.url}/plans/{plan_obj.plan}")
            for b in chain(
                plan_obj.passing(),
                plan_obj.warning(),
                plan_obj.failing(),
                plan_obj.errors(),
                plan_obj.canceled(),
                plan_obj.unknown(),
            ):
                format_plan_result(b, plan_obj._tests_wait_for(b.uid))
            # TODO: print stand alone tests

            (build_summary, test_summary) = plan_summary(plan_obj)
            print(build_summary)
            print(test_summary)
        if oebuild:
            results.uid = oebuild
            result_json, tuxapi_oebuild_url = results.get_oebuild()
            format_result(result_json, tuxapi_oebuild_url)

    except tuxsuite.exceptions.URLNotFound as e:
        error(str(e))

    if cmdargs.json_out:
        cmdargs.json_out.write(json.dumps(result_json, sort_keys=True, indent=4))


handlers = {
    "fetch": handle_fetch,
}


def results_cmd_options(sp):
    sp.add_argument("--build", help="UID of the build to fetch result")
    sp.add_argument("--test", help="UID of the test to fetch result")
    sp.add_argument("--plan", help="UID of the plan to fetch result")
    sp.add_argument("--oebuild", help="UID of the oebuild to fetch result")
    sp.add_argument(
        "--from-json",
        help="Read status input from named json file path",
        type=argparse.FileType("r", encoding="utf-8"),
    )
    sp.add_argument(
        "--json-out",
        help="Write json results out to a named file path",
        type=argparse.FileType("w", encoding="utf-8"),
    )


def setup_parser(parser):
    t = parser.add_parser("fetch")
    results_cmd_options(t)

    return sorted(parser._name_parser_map.keys())
