# -*- coding: utf-8 -*-

import argparse
import json

from tuxsuite.cli.requests import get, post


def handle_add(options, _, config):
    ret = post(
        config, f"/v1/groups/{config.group}/projects", data={"name": options.name}
    )
    if ret.status_code != 201:
        raise NotImplementedError()
    return 0


def handle_get(options, _, config):
    ret = get(config, f"/v1/groups/{config.group}/projects/{options.name}")
    if ret.status_code != 200:
        raise NotImplementedError()

    if options.json:
        print(json.dumps(ret.json()))
    elif options.json_out:
        options.json_out.write(json.dumps(ret.json(), indent=4))
    else:

        def tripplet(d):
            return f"{d['daily']} / {d['monthly']} / {d['overall']}"

        prj = ret.json()
        print(f"name    : {prj['name']}")
        print(f"builds  : {tripplet(prj['builds'])}")
        print(f"oebuilds: {tripplet(prj['oebuilds'])}")
        print(f"plans   : {tripplet(prj['plans'])}")
        print(f"tests   : {tripplet(prj['tests'])}")
        print(
            f"duration: builds={prj['duration']['builds']} tests={prj['duration']['tests']}"
        )
    return 0


def handle_list(options, _, config):
    ret = get(config, f"/v1/groups/{config.group}/projects")
    if ret.status_code != 200:
        raise NotImplementedError()

    if options.json:
        print(json.dumps(ret.json()))
    elif options.json_out:
        options.json_out.write(json.dumps(ret.json(), indent=4))
    else:
        for prj in ret.json()["results"]:
            print(f"* {prj['name']}")
    return 0


handlers = {
    "add": handle_add,
    "get": handle_get,
    "list": handle_list,
}


def setup_parser(parser):
    # "project add <name>"
    p = parser.add_parser("add")
    p.add_argument("name")

    # "project get <name>"
    p = parser.add_parser("get")
    p.add_argument("name")
    p.add_argument("--json", action="store_true", help="Output json project to stdout")
    p.add_argument(
        "--json-out",
        help="Write json project out to a named file path",
        type=argparse.FileType("w", encoding="utf-8"),
    )

    # "project list"
    p = parser.add_parser("list")
    p.add_argument(
        "--json", action="store_true", help="Output json project list to stdout"
    )
    p.add_argument(
        "--json-out",
        help="Write json project list out to a named file path",
        type=argparse.FileType("w", encoding="utf-8"),
    )

    return sorted(parser._name_parser_map.keys())
