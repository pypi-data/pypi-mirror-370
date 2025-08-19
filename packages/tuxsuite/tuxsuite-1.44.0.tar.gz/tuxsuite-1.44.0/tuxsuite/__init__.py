# -*- coding: utf-8 -*-


"""
This is the tuxsuite module.
"""

__version__ = "1.44.0"


from . import build
from . import config
from . import schema, exceptions

from abc import ABC, abstractmethod
from copy import deepcopy
import logging
import fnmatch


logging.basicConfig(format="%(levelname)s: %(message)s")


__config__ = None


def load_config():
    global __config__
    if not __config__:
        __config__ = config.Config()
    return __config__


class Configurable:
    """
    This class loads the configuration.
    """

    def __init__(self, *args, **kwargs):
        cfg = load_config()
        if "token" not in kwargs:
            kwargs["token"] = cfg.auth_token
        if "kbapi_url" not in kwargs:
            kwargs["kbapi_url"] = cfg.kbapi_url
        if "tuxapi_url" not in kwargs:
            kwargs["tuxapi_url"] = cfg.tuxapi_url
        if "group" not in kwargs:
            kwargs["group"] = cfg.group
        if "project" not in kwargs:
            kwargs["project"] = cfg.project
        super().__init__(*args, **kwargs)


class TestConfigurable:
    """
    This class loads the configuration for Test.
    """

    def __init__(self, *args, **kwargs):
        cfg = load_config()
        if "token" not in kwargs:
            kwargs["token"] = cfg.auth_token
        if "kbapi_url" not in kwargs:
            kwargs["kbapi_url"] = cfg.kbapi_url
        if "tuxapi_url" not in kwargs:
            kwargs["tuxapi_url"] = cfg.tuxapi_url
        if "group" not in kwargs:
            kwargs["group"] = cfg.group
        if "project" not in kwargs:
            kwargs["project"] = cfg.project
        if "lava_test_plans_project" not in kwargs:
            kwargs["lava_test_plans_project"] = cfg.lava_test_plans_project
        if "lab" not in kwargs:
            kwargs["lab"] = cfg.lab
        super().__init__(*args, **kwargs)


class Build(Configurable, build.Build):
    """
    This class represents individual builds. It should be used to trigger
    builds, and optionally wait for them to finish.
    """


class Bitbake(Configurable, build.Bitbake):
    """
    This class represents individual builds. It should be used to trigger
    builds, and optionally wait for them to finish.
    """


class Plan(TestConfigurable, build.Plan):
    """
    This class represent a test plan.
    """


class Test(TestConfigurable, build.Test):
    """
    This class represents individual tests. It should be used to trigger
    tests, and optionally wait for them to finish.
    """


class Results(TestConfigurable, build.Results):
    """
    This class represents individual results. It should be used to get results.
    """


class PlanType(ABC):
    """
    This class represents as Base class for all existing and upcoming different types of plans
    """

    plan_cfg = None

    @classmethod
    def load_plan(cls, config):
        if config and config.get("jobs"):
            # setting class variable plan_cfg to hold config data for respective plan type class
            cls.plan_cfg = config
            config_job = config["jobs"][0]
            # checking if it is bake plan
            if "bake" in config_job or "bakes" in config_job:
                return BakePlan()
            elif any(
                [
                    True if item in config_job else False
                    for item in ["build", "builds", "test", "tests", "sanity_test"]
                ]
            ):
                return BuildPlan()
            else:
                raise exceptions.UnsupportedJob("Unsupported jobtype")
        else:
            raise exceptions.InvalidConfiguration(
                "Plan configuration file must contain Jobs"
            )

    def count(self, plan):
        count = 0
        for cfg in plan.config.plan:
            if cfg.get("build"):
                count += 1
            if cfg.get("tests"):
                count += len(cfg["tests"])
            if cfg.get("sanity_test"):
                count += 1
        return count

    @abstractmethod
    def check_schema(self):
        pass

    @abstractmethod
    def apply(self):
        pass

    @abstractmethod
    def plan_info(self):
        pass

    @abstractmethod
    def create_builds(self):
        pass


class BuildPlan(PlanType):
    name = "BUILD"

    def check_schema(self, config):
        return schema.plan()(config)

    def apply(self, plan_config):
        for cfg in PlanType.plan_cfg["jobs"]:
            if plan_config.job_name is not None and not [
                name
                for name in plan_config.job_name
                if fnmatch.fnmatch(cfg.get("name", ""), name)
            ]:
                continue
            builds = []
            if "build" in cfg:
                builds = [cfg["build"]]
            elif "builds" in cfg:
                builds = cfg["builds"]
            # check sanity_test
            sanity_test = {}
            if "sanity_test" in cfg:
                sanity_test = cfg["sanity_test"]
            tests = []
            if "test" in cfg:
                tests = [cfg["test"]]
            elif "tests" in cfg:
                tests = cfg["tests"]
            new_tests = []
            for test in tests:
                if "sharding" in test:
                    sharding = test.pop("sharding")
                    for i in range(1, sharding + 1):
                        t = deepcopy(test)
                        t.setdefault("parameters", {})
                        t["parameters"]["SHARD_NUMBER"] = sharding
                        t["parameters"]["SHARD_INDEX"] = i
                        new_tests.append(t)
                else:
                    new_tests.append(test)
            tests = new_tests

            if builds:
                for build_item in builds:
                    plan_config.plan.append(
                        {
                            "build": build_item,
                            "tests": tests,
                            "sanity_test": sanity_test,
                        }
                    )
            else:
                plan_config.plan.append(
                    {"build": None, "tests": tests, "sanity_test": sanity_test}
                )

    def plan_info(self, name, description):
        print("Running Linux Kernel plan '{}': '{}'".format(name, description))

    def create_builds(self, plan, builds):
        for cfg in plan.config.plan:
            if cfg["build"] is not None:
                data = plan.args.copy()
                # Ignore bake plan options
                data.pop("manifest_file", None)
                data.pop("pinned_manifest", None)
                data.pop("kas_override", None)
                data.pop("lava_test_plans_project", None)
                data.pop("lab", None)
                data.pop("plan_callback", None)
                data.pop("plan_callback_headers", None)
                data.pop("parameters", None)

                # Remove notify_emails
                data.pop("notify_emails", None)

                data.update(cfg["build"])
                if plan.args.get("no_cache"):
                    data["no_cache"] = True
                builds.append(build.Build(**data))
            else:
                builds.append(None)

        builds_to_submit = [b for b in builds if b]
        if builds_to_submit:
            req_data = {"builds": [], "patches": {}}
            for b in builds_to_submit:
                build_entry, patch = b.generate_build_request(plan=plan.plan)
                req_data["builds"].append(build_entry)
                req_data["patches"].update(patch)

            # submit in batches of 500 to prevent tuxapi lambda time out
            ret = []
            for i in range(0, len(req_data["builds"]), 500):
                batch_data = {
                    "builds": req_data["builds"][i : i + 500],
                    "patches": req_data["patches"],
                }
                ret += build.post_request(
                    f"{plan.url}/builds", plan.headers, batch_data
                )
            # Updating builds_to_submit will update values in builds
            for build_obj, data in zip(builds_to_submit, ret):
                build_obj.build_data = f"{plan.url}/builds/{data['uid']}"
                build_obj.uid = data["uid"]
                build_obj.status = data


class BakePlan(PlanType):
    name = "OEBUILD"

    def check_schema(self, config):
        return schema.bake_plan()(config)

    def apply(self, plan_config):
        for cfg in PlanType.plan_cfg["jobs"]:
            if plan_config.job_name is not None and not [
                name
                for name in plan_config.job_name
                if fnmatch.fnmatch(cfg.get("name", ""), name)
            ]:
                continue
            builds = []
            if "bake" in cfg:
                builds = [cfg["bake"]]
            elif "bakes" in cfg:
                builds = cfg["bakes"]
            tests = []
            if "test" in cfg:
                tests = [cfg["test"]]
            elif "tests" in cfg:
                tests = cfg["tests"]
            new_tests = []
            for test in tests:
                if "sharding" in test:
                    sharding = test.pop("sharding")
                    for i in range(1, sharding + 1):
                        t = deepcopy(test)
                        t.setdefault("parameters", {})
                        t["parameters"]["SHARD_NUMBER"] = sharding
                        t["parameters"]["SHARD_INDEX"] = i
                        new_tests.append(t)
                else:
                    new_tests.append(test)
            tests = new_tests

            if builds:
                for build_item in builds:
                    plan_config.plan.append({"build": build_item, "tests": tests})
            else:
                plan_config.plan.append({"build": None, "tests": tests})

    def plan_info(self, name, description):
        print("Running Bake plan '{}': '{}'".format(name, description))

    def create_builds(self, plan, builds):
        req_data = {"oebuilds": [], "manifests": {}}
        # handling options
        no_cache = plan.args.get("no_cache", False)
        is_public = plan.args.get("is_public", True)
        callback = plan.args.get("callback")
        callback_headers = plan.args.get("callback_headers")
        plan_files = {
            "manifest_file": plan.args.get("manifest_file"),
            "pinned_manifest": plan.args.get("pinned_manifest"),
            "kas_override": plan.args.get("kas_override"),
        }

        # filtering out Bitbake Child class (BuildDefiniton) attributes
        data = {
            key: value
            for key, value in plan.args.items()
            if key
            not in [
                "git_repo",
                "git_sha",
                "git_ref",
                "no_cache",
                "patch_series",
                "is_public",
                "callback",
                "callback_headers",
                "lava_test_plans_project",
                "lab",
                "plan_callback",
                "plan_callback_headers",
                "parameters",
                "notify_emails",
                *plan_files,
            ]
        }

        # handling manifest ( either pinned or local manifest)
        for file in plan_files:
            if plan_files[file] is not None:
                if file in ["kas_override"]:
                    file_type = "yaml"
                else:
                    file_type = "xml"
                encoded_name, file_content = build.handle_attachment(
                    plan_files[file], file_type=file_type
                )
                req_data["manifests"].update({encoded_name: file_content})
                plan_files[file] = encoded_name

        for cfg in plan.config.plan:
            if cfg["build"] is not None:
                data["data"] = cfg["build"]
                data["data"]["no_cache"] = no_cache
                data["data"]["manifest_file"] = plan_files["manifest_file"]
                data["data"]["pinned_manifest"] = plan_files["pinned_manifest"]
                data["data"]["kas_override"] = plan_files["kas_override"]
                data["data"]["is_public"] = is_public
                data["data"]["callback"] = cfg["build"].get("callback", callback)
                data["data"]["callback_headers"] = cfg["build"].get(
                    "callback_header", callback_headers
                )
                builds.append(build.Bitbake(**data))
            else:
                builds.append(None)

        builds_to_submit = [b for b in builds if b]
        if builds_to_submit:
            for b in builds_to_submit:
                build_entry, _ = b.generate_build_request(plan=plan.plan)
                req_data["oebuilds"].append(build_entry)

            # submit in batches of 500 to prevent tuxapi lambda time out
            ret = []
            for i in range(0, len(req_data["oebuilds"]), 500):
                batch_data = {
                    "oebuilds": req_data["oebuilds"][i : i + 500],
                    "manifests": req_data["manifests"],
                }
                ret += build.post_request(
                    f"{plan.url}/oebuilds", plan.headers, batch_data
                )
            # Updating builds_to_submit will update values in builds
            for bake_obj, data in zip(builds_to_submit, ret):
                bake_obj.build_data = f"{plan.url}/oebuilds/{data['uid']}"
                bake_obj.uid = data["uid"]
                bake_obj.status = data
