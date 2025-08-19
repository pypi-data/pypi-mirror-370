# -*- coding: utf-8 -*-

import argparse
import csv
import json
import sys

from tuxsuite.cli.models import Bill, Group
from tuxsuite.cli.requests import get


def format_int(v):
    if v > 1e6:
        return f"{int(v // 1e6)}M"
    if v > 1e3:
        return f"{int(v // 1e3)}k"
    return str(v)


def handle_bills(options, _, config):
    ret = get(config, f"/v1/groups/{options.name}/bills")
    if ret.status_code != 200:
        raise NotImplementedError()

    bills = (Bill.new(**b) for b in ret.json()["results"])
    if options.csv:
        fields = [
            "date",
            "builds",
            "oebuilds",
            "plans",
            "tests",
            "builds.duration",
            "oebuilds.duration",
            "tests.duration",
        ]
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        for bill in bills:
            writer.writerow(
                {
                    "date": bill.date,
                    "plans": bill.count.plans,
                    "builds": bill.count.builds,
                    "oebuilds": bill.count.oebuilds,
                    "tests": bill.count.tests,
                    "builds.duration": bill.duration.builds,
                    "oebuilds.duration": bill.duration.oebuilds,
                    "tests.duration": bill.duration.tests,
                }
            )
    elif options.json:
        print(json.dumps(ret.json()))
    elif options.json_out:
        options.json_out.write(json.dumps(ret.json(), indent=4))
    else:
        print("date\t\tbuilds\toe\tplans\ttests\tbuilds\toe\ttests")
        for bill in bills:
            builds = bill.count.builds
            oebuilds = bill.count.oebuilds
            plans = bill.count.plans
            tests = bill.count.tests
            d_builds = format_int(bill.duration.builds)
            d_oebuilds = format_int(bill.duration.oebuilds)
            d_tests = format_int(bill.duration.tests)
            print(
                f"{bill.date}\t{builds}\t{oebuilds}\t{plans}\t{tests}\t{d_builds}\t{d_oebuilds}\t{d_tests}"
            )
    return 0


def handle_get(options, _, config):
    ret = get(config, f"/v1/groups/{options.name}")
    if ret.status_code != 200:
        raise NotImplementedError()

    if options.json:
        print(json.dumps(ret.json()))
    elif options.json_out:
        options.json_out.write(json.dumps(ret.json(), indent=4))
    else:

        def tripplet(d):
            return f"{d.daily} / {d.monthly} / {d.overall}"

        grp = Group.new(**ret.json())
        print(f"name    : {grp.name}")
        print(f"builds  : {tripplet(grp.builds)}")
        print(f"oebuilds  : {tripplet(grp.oebuilds)}")
        print(f"plans   : {tripplet(grp.plans)}")
        print(f"tests   : {tripplet(grp.tests)}")
        print(f"duration: builds={grp.duration.builds} tests={grp.duration.tests}")
        print(
            f"limits  : {grp.limits.builds} / {grp.limits.oebuilds} / {grp.limits.tests}"
        )
        print(f"devices : {', '.join(grp.lava_devices)}")
    return 0


def handle_list(options, _, config):
    ret = get(config, "/v1/groups")
    if ret.status_code != 200:
        raise NotImplementedError()

    if options.json:
        print(json.dumps(ret.json()))
    elif options.json_out:
        options.json_out.write(json.dumps(ret.json(), indent=4))
    else:
        print("groups:")
        for grp in ret.json()["results"]:
            print(f"* {grp}")
    return 0


handlers = {
    "bills": handle_bills,
    "get": handle_get,
    "list": handle_list,
}


def setup_parser(parser):
    # "group bills <name>"
    p = parser.add_parser("bills")
    p.add_argument("name")
    p.add_argument("--csv", action="store_true")
    p.add_argument("--json", action="store_true", help="Output json bills to stdout")
    p.add_argument(
        "--json-out",
        help="Write json bills out to a named file path",
        type=argparse.FileType("w", encoding="utf-8"),
    )
    # "group get <name>"
    p = parser.add_parser("get")
    p.add_argument("name")
    p.add_argument("--json", action="store_true", help="Output json group to stdout")
    p.add_argument(
        "--json-out",
        help="Write json group out to a named file path",
        type=argparse.FileType("w", encoding="utf-8"),
    )
    # "group list"
    p = parser.add_parser("list")
    p.add_argument(
        "--json", action="store_true", help="Output json group list to stdout"
    )
    p.add_argument(
        "--json-out",
        help="Write json group list out to a named file path",
        type=argparse.FileType("w", encoding="utf-8"),
    )

    return sorted(parser._name_parser_map.keys())
