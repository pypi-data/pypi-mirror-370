# -*- coding: utf-8 -*-

"""
This is the tuxsuite command.
"""


import argparse
import contextlib
import sys

from tuxsuite import __version__
from tuxsuite.cli.config import load_config
from tuxsuite.cli.utils import error, get_remote_version
from tuxsuite.cli.bake import (
    handlers as bake_handlers,
    setup_parser as bake_parser,
)
from tuxsuite.cli.build import (
    handlers as build_handlers,
    setup_parser as build_parser,
)
from tuxsuite.cli.group import (
    handlers as group_handlers,
    setup_parser as group_parser,
)
from tuxsuite.cli.plan import (
    handlers as plan_handlers,
    setup_parser as plan_parser,
)
from tuxsuite.cli.project import (
    handlers as project_handlers,
    setup_parser as project_parser,
)
from tuxsuite.cli.test import (
    handlers as test_handlers,
    setup_parser as test_parser,
)
from tuxsuite.cli.results import (
    handlers as results_handlers,
    setup_parser as results_parser,
)
from tuxsuite.cli.keys import (
    handlers as keys_handlers,
    setup_parser as keys_parser,
)
from tuxsuite.cli.trigger import (
    handlers as trigger_handlers,
    setup_parser as trigger_parser,
)


def setup_parser():
    parser = argparse.ArgumentParser(
        prog="tuxsuite",
        description="The TuxSuite CLI is the supported interface to TuxBuild and TuxTest.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s, {__version__}"
    )

    parser.add_argument(
        "--remote-version",
        help="show remote backend tools version",
        default=False,
        action="store_true",
    )

    sub_parser = parser.add_subparsers(dest="command", help="Command")
    sub_parser.required = True

    bake = sub_parser.add_parser(
        "bake",
        help="Do an OE/Yocto build with bitbake like 'tuxsuite bake submit <build-definition.yaml>'",
    ).add_subparsers(dest="sub_command", help="Commands")
    bake.required = True
    bake_cmds = bake_parser(bake)

    build = sub_parser.add_parser("build", help="Run a single build.").add_subparsers(
        dest="sub_command", help="Commands"
    )
    build.required = True
    build_cmds = build_parser(build)

    group = sub_parser.add_parser("group", help="Manage group.").add_subparsers(
        dest="sub_command", help="Commands"
    )
    group.required = True
    group_cmds = group_parser(group)

    plan = sub_parser.add_parser("plan", help="Run a plan file.").add_subparsers(
        dest="sub_command", help="Commands"
    )
    plan.required = True
    plan_cmds = plan_parser(plan)

    project = sub_parser.add_parser("project", help="Manage project.").add_subparsers(
        dest="sub_command", help="Commands"
    )
    project.required = True
    project_cmds = project_parser(project)

    test = sub_parser.add_parser("test", help="Test a kernel.").add_subparsers(
        dest="sub_command", help="Commands"
    )
    test.required = True
    test_cmds = test_parser(test)

    results = sub_parser.add_parser("results", help="Fetch results.").add_subparsers(
        dest="sub_command", help="Commands"
    )
    results.required = True
    results_cmds = results_parser(results)

    keys = sub_parser.add_parser("keys", help="Keys.").add_subparsers(
        dest="sub_command", help="Commands"
    )
    keys.required = True
    keys_cmds = keys_parser(keys)

    trigger = sub_parser.add_parser("trigger", help="Trigger.").add_subparsers(
        dest="sub_command", help="Commands"
    )
    trigger.required = True
    trigger_cmds = trigger_parser(trigger)

    return (
        parser,
        {
            "bake": bake_cmds,
            "build": build_cmds,
            "group": group_cmds,
            "keys": keys_cmds,
            "plan": plan_cmds,
            "project": project_cmds,
            "test": test_cmds,
            "results": results_cmds,
            "trigger": trigger_cmds,
        },
    )


def main():
    (parser, cmds) = setup_parser()

    if "--help" not in sys.argv and "-h" not in sys.argv:
        with contextlib.suppress(IndexError):
            if sys.argv[1] == "results" and sys.argv[2] not in cmds["results"]:
                sys.argv.insert(2, "fetch")
            elif sys.argv[1] == "build" and sys.argv[2] not in cmds["build"]:
                sys.argv.insert(2, "submit")
            elif sys.argv[1] == "plan" and sys.argv[2] not in cmds["plan"]:
                sys.argv.insert(2, "submit")
            elif sys.argv[1] == "test" and sys.argv[2] not in cmds["test"]:
                sys.argv.insert(2, "submit")

    # fetch remote backend tools version
    if "--remote-version" in sys.argv:
        versions = get_remote_version(load_config())
        print(
            f"tuxbake: {versions.get('versions').get('tuxbake')}\n"
            f"tuxmake: {versions.get('versions').get('tuxmake')}\n"
            f"tuxrun: {versions.get('versions').get('tuxrun')}"
        )
        sys.exit(0)

    (options, extra_arguments) = parser.parse_known_args()

    # SPECIAL CASE: "tuxsuite plan create|execute" sub-sub-command does not require
    # the config in order to generate / create a plan file / run a plan locally
    if options.command == "plan" and options.sub_command == "create":
        return plan_handlers[options.sub_command](options, extra_arguments)

    if options.command == "plan" and options.sub_command == "execute":
        return plan_handlers[options.sub_command](options, extra_arguments)

    cfg = load_config()
    # Handle command
    if options.command == "results":
        return results_handlers[options.sub_command](options, extra_arguments, cfg)
    elif options.command == "bake":
        return bake_handlers[options.sub_command](options, extra_arguments, cfg)
    elif options.command == "build":
        return build_handlers[options.sub_command](options, extra_arguments, cfg)
    elif options.command == "group":
        return group_handlers[options.sub_command](options, extra_arguments, cfg)
    elif options.command == "test":
        return test_handlers[options.sub_command](options, extra_arguments, cfg)
    elif options.command == "plan":
        return plan_handlers[options.sub_command](options, extra_arguments, cfg)
    elif options.command == "project":
        return project_handlers[options.sub_command](options, extra_arguments, cfg)
    elif options.command == "keys":
        return keys_handlers[options.sub_command](options, extra_arguments, cfg)
    elif options.command == "trigger":
        return trigger_handlers[options.sub_command](options, extra_arguments, cfg)
    else:
        error("Unknown sub command")
        sys.exit(2)


if __name__ == "__main__":
    sys.exit(main())
