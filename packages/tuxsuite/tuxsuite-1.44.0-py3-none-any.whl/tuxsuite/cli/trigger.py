# -*- coding: utf-8 -*-
import os
import sys
import yaml
import glob


from tuxsuite.utils import error
from tuxsuite.cli.requests import (
    delete,
    get,
    post,
)
from tuxsuite.cli.utils import file_or_url
from tuxsuite.schema import plan, tuxtrigger_config, SchemaError


def validate_schema(data, file_type: str):
    if file_type == "config":
        return tuxtrigger_config()(data)
    elif file_type == "plan":
        return plan()(data)


def load_yaml(path, file_type: str):
    try:
        contents = open(path).read()
        yaml_data = yaml.safe_load(contents)
        validate_schema(yaml_data, file_type)
        name_ext = os.path.basename(path)
        name = name_ext.split(".")[0]
        return (name, contents)
    except (FileNotFoundError, yaml.YAMLError, SchemaError) as exc:
        error(f"Invalid {file_type} file: {str(exc)}")


def handle_add(cmdargs, _, config):
    data = {"config": {}, "plans": []}
    url = f"/v1/groups/{config.group}/projects/{config.project}/tuxtrigger"

    if not cmdargs.config and not cmdargs.plan:
        error("Either config or plan must be provided")

    if cmdargs.config:
        name, config_data = load_yaml(cmdargs.config, "config")
        data["config"] = config_data

    if cmdargs.plan:
        if os.path.isfile(cmdargs.plan):
            name, plan_data = load_yaml(cmdargs.plan, "plan")
            data["plans"].append((name, plan_data))
        else:
            # get all plan files at {plan} folder
            plan_path = cmdargs.plan
            files = glob.glob(plan_path + "/*.yaml")
            for plan_file in files:
                name, plan_data = load_yaml(plan_file, "plan")
                data["plans"].append((name, plan_data))

    ret = post(config, url, data=data)

    if ret.status_code != 201:
        error(
            f"Failed to add tuxtrigger 'config/plan'. {ret.json().get('error', '')}".strip()
        )
    else:
        print("Tuxtrigger 'config/plan' files added")
        sys.exit(0)


def handle_get(cmdargs, _, config):
    params = {"config": cmdargs.config, "plan": cmdargs.plan}
    url = f"/v1/groups/{config.group}/projects/{config.project}/tuxtrigger"
    ret = get(config, url, params=params)

    if ret.status_code != 200:
        error("Failed to get the tuxtrigger config/plan. Is config/plan exists! ?")
    else:
        tuxtrigger = ret.json()
        if not cmdargs.config and cmdargs.plan is None:
            cfg, plans = tuxtrigger.get("config"), tuxtrigger.get("plans")
            if cfg:
                print("Tuxtrigger config:\n# config.yaml\n")
            if plans:
                print("Tuxtrigger plans:")
                for count, item in enumerate(plans, start=1):
                    print(f"{count}. {item}")
            if not any([cfg, plans]):
                print("No config or plan file present!!")
        else:
            # If provided config or plan, then show data
            if cmdargs.config:
                print(tuxtrigger.get("config", "").strip())
            elif cmdargs.plan:
                print(tuxtrigger.get("plan", "").strip())

        sys.exit(0)


def handle_delete(cmdargs, _, config):
    data = {"config": False, "plans": []}
    url = f"/v1/groups/{config.group}/projects/{config.project}/tuxtrigger"

    if not cmdargs.config and not cmdargs.plans:
        error("Either config or plan must be provided for deletion")

    msg = ""
    if cmdargs.config:
        data["config"] = True
        msg += "Config: config.yaml"
    if cmdargs.plans:
        data["plans"] = cmdargs.plans
        msg += f" Plan: {','.join(data['plans'])}"

    ret = delete(config, url, data=data)
    if ret.status_code != 200:
        error(f"Failed to delete {msg.strip()} file")
    else:
        print(f"{msg.strip()} file deleted")
        sys.exit(0)


handlers = {
    "add": handle_add,
    "get": handle_get,
    "delete": handle_delete,
}


def trigger_add_options(sp):
    sp.add_argument(
        "--config",
        help="Path to the tuxtrigger config file",
        default=None,
        type=file_or_url,
    )
    sp.add_argument(
        "--plan",
        help="Path to the tuxtrigger plan file/directory",
        default=None,
        type=file_or_url,
    )


def trigger_delete_options(sp):
    sp.add_argument("--config", action="store_true", help="Delete config file")
    sp.add_argument(
        "--plan",
        help="Name of the plan file to be deleted. Can be specified multiple times",
        default=[],
        action="append",
        dest="plans",
    )


def trigger_get_options(sp):
    grp = sp.add_mutually_exclusive_group(required=False)
    grp.add_argument("--config", action="store_true", help="Show config file")
    grp.add_argument(
        "--plan",
        help="Name of the plan file to be shown",
        default=None,
    )


def setup_parser(parser):
    # "trigger add"
    t = parser.add_parser("add")
    trigger_add_options(t)

    # "trigger get"
    t = parser.add_parser("get")
    trigger_get_options(t)

    # "trigger delete"
    t = parser.add_parser("delete")
    trigger_delete_options(t)

    return sorted(parser._name_parser_map.keys())
