# -*- coding: utf-8 -*-

import argparse
import sys
import json

from tuxsuite.utils import error
from tuxsuite.cli.requests import (
    delete,
    get,
    post,
    put,
)


# keys available kinds with their arguments
KIND = {
    "pat": ["domain", "username", "token"],
    "variables": ["keyname", "type", "value"],
}


def display_keys(keys):
    for kind in KIND:
        kind_keys = keys.get(kind)
        if kind_keys:
            print(f"{kind} keys:\n")
            print("{:<10} {:<25} {:<25} {:<10}\n".format(*(["S.no"] + KIND[kind])))
            for count, item in enumerate(kind_keys, start=1):
                values = [item[val] for val in KIND[kind]]
                print("{:<10} {:<25} {:<25} {:<10}".format(*([str(count)] + values)))
            print()


def check_required_cmdargs(cmdargs, required_args=None):
    # check keys args and return updated cmdargs
    key_type = cmdargs.type
    if key_type != "pat":
        key_type, key_kind = key_type.split(":")
        cmdargs.type = "file" if key_kind == "file" else "variable"
        if cmdargs.sub_command != "delete":
            keyname, value = key_value(cmdargs.variables)
            cmdargs.keyname = keyname
            cmdargs.value = value
    cmdargs.kind = key_type
    if required_args is None:
        required_args = KIND[key_type]
    for item in required_args:
        if getattr(cmdargs, item) is None:
            error(f"--{item} is required for key type '{key_type}'")


def handle_add(cmdargs, _, config):
    check_required_cmdargs(cmdargs)
    kind = cmdargs.kind
    data = {"key": {}}
    url = f"/v1/groups/{config.group}/projects/{config.project}/keys"
    data["kind"] = kind
    for item in KIND[kind]:
        data["key"][item] = getattr(cmdargs, item)

    ret = post(config, url, data=data)
    msg = (
        f"{cmdargs.domain}:{cmdargs.username}"
        if kind == "pat"
        else f"{cmdargs.keyname}:{cmdargs.type}"
    )

    if ret.status_code != 201:
        error(
            f"Failed to add '{kind}' key '{msg}'. {ret.json().get('error', '')}".strip()
        )
    else:
        print(f"'{kind}' key '{msg}' added")
        sys.exit(0)


def handle_get(cmdargs, _, config):
    url = f"/v1/groups/{config.group}/projects/{config.project}/keys"
    ret = get(config, url)

    if ret.status_code != 200:
        error("Failed to get the keys")
    else:
        keys = ret.json()
        # change variable types to variables:(env|file)
        for key in keys.get("variables", {}):
            if key["type"] == "file":
                key["type"] = "variables:file"
            else:
                key["type"] = "variables:env"

        if cmdargs.json:
            print(json.dumps(keys, indent=True))
        elif cmdargs.json_out:
            cmdargs.json_out.write(json.dumps(keys, indent=4))
        else:
            print(f"ssh public key:\n\n{keys['ssh']['pub']}\n")
            display_keys(keys)
        sys.exit(0)


def handle_delete(cmdargs, _, config):
    data = {"key": {}}
    msg = ""
    url = f"/v1/groups/{config.group}/projects/{config.project}/keys"
    if cmdargs.type == "pat":
        required_args = ["domain", "username"]
        msg = f"{cmdargs.domain}:{cmdargs.username}"
    elif cmdargs.type in ["variables:env", "variables:file"]:
        if not cmdargs.keyname:
            error("KEYNAME is required for type variables")
        required_args = ["keyname"]
        msg = f"{cmdargs.keyname}"
    check_required_cmdargs(cmdargs, required_args)
    kind = cmdargs.kind
    data["kind"] = kind
    for item in required_args:
        data["key"][item] = getattr(cmdargs, item)

    ret = delete(config, url, data=data)
    if ret.status_code != 200:
        error(f"Failed to delete '{kind}' key '{msg}'")
    else:
        print(f"'{kind}' key '{msg}' deleted")
        sys.exit(0)


def handle_update(cmdargs, _, config):
    data = {"key": {}}
    url = f"/v1/groups/{config.group}/projects/{config.project}/keys"
    check_required_cmdargs(cmdargs)
    kind = cmdargs.kind
    data["kind"] = kind
    for item in KIND[kind]:
        data["key"][item] = getattr(cmdargs, item)

    msg = (
        f"{cmdargs.domain}:{cmdargs.username}"
        if kind == "pat"
        else f"{cmdargs.keyname}:{cmdargs.type}"
    )
    ret = put(config, url, data=data)

    if ret.status_code != 201:
        error(f"Failed to update '{kind}' key '{msg}'")
    else:
        print(f"'{kind}' key '{msg}' updated")
        sys.exit(0)


handlers = {
    "add": handle_add,
    "get": handle_get,
    "delete": handle_delete,
    "update": handle_update,
}


def key_value(s):
    if not s:
        error("missing key value pair, please provide key value in 'KEY=VALUE' format")
    if s.count("=") != 1:
        error("Key value pair not valid, must be in 'KEY=VALUE' format")
    return s.split("=")


def keys_cmd_common_options(sp):
    sp.add_argument(
        "--type",
        choices=["pat", "variables:env", "variables:file"],
        help="Kind of the key",
        required=True,
    )
    # type "pat" arguments
    pat_group = sp.add_argument_group("pat type options")
    pat_group.add_argument(
        "--domain",
        help="Domain for the given key",
        default=None,
        type=str,
    )
    pat_group.add_argument(
        "--username",
        help="Username for the given key",
        default=None,
        type=str,
    )

    variables_group = sp.add_argument_group("variables type options")

    return (pat_group, variables_group)


def keys_cmd_variable(sp):
    sp.add_argument(
        "variables",
        help="Variable in 'KEY=VALUE' format",
        nargs="?",
        default="",
    )


def keys_cmd_variable_keyname(sp):
    sp.add_argument(
        "keyname",
        help="Keyname for the given key",
        nargs="?",
        default=None,
    )


def keys_cmd_token_option(sp):
    sp.add_argument(
        "--token",
        help="Value of the Personal Access Token (PAT)",
        default=None,
        type=str,
    )


def setup_parser(parser):
    # "keys add"
    t = parser.add_parser("add")
    pat, variable = keys_cmd_common_options(t)
    keys_cmd_token_option(pat)
    keys_cmd_variable(variable)

    # "keys get"
    t = parser.add_parser("get")
    t.add_argument(
        "--json",
        help="Output json keys to stdout",
        default=False,
        action="store_true",
    )
    t.add_argument(
        "--json-out",
        help="Write json keys out to a named file path",
        type=argparse.FileType("w", encoding="utf-8"),
    )

    # "keys delete"
    t = parser.add_parser("delete")
    _, variable = keys_cmd_common_options(t)
    keys_cmd_variable_keyname(variable)

    # "keys update"
    t = parser.add_parser("update")
    pat, variable = keys_cmd_common_options(t)
    keys_cmd_token_option(pat)
    keys_cmd_variable(variable)

    return sorted(parser._name_parser_map.keys())
