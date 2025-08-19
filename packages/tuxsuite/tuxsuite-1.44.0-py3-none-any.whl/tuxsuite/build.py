# -*- coding: utf-8 -*-

from attr import attrs, attrib
import base64
import hashlib
import json
import mimetypes
import os
import pathlib
import random
import re
import sys
import shutil
import subprocess
import tarfile
import tempfile
import time
import yaml
import xml.etree.ElementTree as ET
import tuxsuite.exceptions
import tuxsuite.requests
from tuxsuite import __version__
import uuid
from urllib.parse import urlparse
from tuxsuite.cli import error


delay_status_update = int(os.getenv("TUXSUITE_DELAY_STATUS_UPDATE", "29")) + 1


def post_request(url, headers, request):
    response = tuxsuite.requests.post(url, data=json.dumps(request), headers=headers)
    if response.ok:
        return json.loads(response.text)
    else:
        if response.status_code in [400, 403]:
            response_data = response.json()
            if "error" in response_data:
                message = response_data["error"]
            else:
                message = response_data.get("status_message")
            raise tuxsuite.exceptions.BadRequest(message)
        else:
            try:
                raise Exception(response.json()["error"])
            except Exception:
                response.raise_for_status()


def get_request(url, headers, params=None):
    response = tuxsuite.requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        if response.status_code == 404:
            raise tuxsuite.exceptions.URLNotFound(response.text)
        response.raise_for_status()  # Some unexpected status that's not caught


def download_patch_with_b4(patch_path):
    if shutil.which("b4"):
        patch_file = os.path.join(
            tempfile.gettempdir(),
            f"{hashlib.sha256(patch_path.encode()).hexdigest()}.mbox",
        )
        patch_file_mbx = os.path.join(
            tempfile.gettempdir(),
            f"{hashlib.sha256(patch_path.encode()).hexdigest()}.mbx",
        )
        if os.path.exists(patch_file):
            m_time = os.path.getctime(patch_file)
            time_delta_seconds = time.time() - m_time
            # Check if the patch file is older than 3 minutes before download
            if time_delta_seconds > 180.0:
                os.remove(patch_file)
                subprocess.check_output(["b4", "am", "-n", patch_file, patch_path])
        else:
            subprocess.check_output(["b4", "am", "-n", patch_file, patch_path])

        # We need this rename from *.mbx to *.mbox, due to a bug in b4,
        # where it always downloads the patch with a *.mbx extension and
        # not with the specified extension
        if os.path.exists(patch_file_mbx):
            os.rename(patch_file_mbx, patch_file)
        patch_path = patch_file
        patch_file = os.path.basename(patch_file)
        return (patch_file, patch_path)
    else:
        print(
            f"\033[91mERROR: 'b4' not found to download patch from {patch_path}\033[0m"
        )
        sys.exit(1)


def handle_patch(patch_path):
    patch_type = None
    patch_is_web_url = False
    patch_content = None
    patch_file = os.path.basename(patch_path)
    if "lore.kernel.org" in patch_path:
        patch_type = "lore"
        patch_file, patch_path = download_patch_with_b4(patch_path)
    elif urlparse(patch_path).scheme in ["http", "https"]:
        patch_type = "url"
    elif os.path.isfile(patch_path):
        patch_type = "file"
    elif os.path.isdir(patch_path):
        patch_type = "dir"
    else:
        patch_type = "message-id"
        patch_file, patch_path = download_patch_with_b4(patch_path)

    if patch_type == "url":
        patch_file = patch_path
        patch_content = b""
        patch_is_web_url = True
    elif patch_type in ["lore", "file", "message-id"]:
        # Rename .mbx to .mbox on the fly.
        if pathlib.Path(patch_path).suffix == ".mbx":
            new_patch_path = os.path.join(
                os.path.dirname(patch_path), pathlib.Path(patch_path).stem + ".mbox"
            )
            os.rename(os.path.abspath(patch_path), new_patch_path)
            patch_path = new_patch_path
        file_type, file_encoding = mimetypes.guess_type(patch_path)
        if file_type in [
            "application/mbox",
            "text/plain",
            "text/x-diff",
            "application/x-tar",
        ]:
            if file_encoding == "gzip":
                series_exists = False
                with tarfile.open(patch_path, "r") as patch:
                    series_exists = "series" in [
                        os.path.basename(f) for f in patch.getnames()
                    ]
                if not series_exists:
                    raise Exception("series file missing in patch archive")
            elif file_encoding is None:  # Valid for mbox format
                pass
            else:
                raise Exception(
                    f"Unsupported patch series archive format: {file_encoding}"
                )
        else:
            raise Exception("Patch series format unknown")
        with open(patch_path, "rb") as patch:
            patch_content = base64.b64encode(patch.read())
    elif patch_type == "dir":
        if not os.path.exists(os.path.join(patch_path, "series")):
            raise Exception("series file not found in patch directory")
        patch_path = os.path.abspath(patch_path)
        patch_file = f"{os.path.basename(patch_path)}.tgz"
        tar_file = os.path.join("/tmp", patch_file)
        with tarfile.open(tar_file, "w:gz") as tar:
            tar.add(patch_path, arcname=os.path.sep)
        with open(tar_file, "rb") as patch:
            patch_content = base64.b64encode(patch.read())
    if not patch_is_web_url:
        patch_sha256 = hashlib.sha256(patch_content).hexdigest()
        patch_file = f"{patch_sha256}/{patch_file}"
    return (patch_file, patch_content.decode("utf-8"))


def handle_attachment(file_path, file_type="xml"):
    file_is_web_url = False
    file_content = None
    filename = os.path.basename(file_path)
    if urlparse(file_path).scheme in ["http", "https"]:
        filename = file_path
        file_content = b""
        file_is_web_url = True
    else:
        ext = os.path.splitext(file_path)[1].lower()
        if os.path.isfile(file_path) and ext in [".xml", ".yml", ".yaml"]:
            if file_type == "yaml" and ext not in [".yml", ".yaml"]:
                error(f"{file_path} does not have yaml file extension")
            elif file_type == "xml" and ext != ".xml":
                error(f"{file_path} does not have xml file extension")
        else:
            error(f"{file_path}: Is provided file a valid xml/yaml file?")
        # extension of file
        with open(file_path, "r") as f:
            try:
                if ext == ".xml":
                    # parse XML file
                    ET.parse(f)
                elif ext in [".yml", ".yaml"]:
                    # parse yaml file
                    yaml.safe_load(f)
            except ET.ParseError as e:
                error(f"Error parsing {file_path} file: {e}")
            except yaml.YAMLError as e:
                error(f"Error parsing {file_path} file: {e}")
        with open(file_path, "rb") as infile:
            file_content = base64.b64encode(infile.read())
    if not file_is_web_url:
        file_sha256 = hashlib.sha256(file_content).hexdigest()
        filename = f"{file_sha256}/{filename}"
    return (filename, file_content.decode("utf-8"))


class HeadersMixin:
    @property
    def headers(self):
        return {
            "User-Agent": "tuxsuite/{}".format(__version__),
            "Content-Type": "application/json",
            "Authorization": self.token,
        }


@attrs(kw_only=True)
class BuildState:
    build = attrib()
    state = attrib()
    status = attrib(default=None)
    message = attrib()
    warnings = attrib(default=0)
    errors = attrib(default=0)
    icon = attrib()
    cli_color = attrib()
    final = attrib(default=False)


@attrs(kw_only=True, order=False)
class Build(HeadersMixin):
    git_repo = attrib()
    git_ref = attrib(default=None)
    git_sha = attrib(default=None)
    target_arch = attrib()
    kconfig = attrib()
    toolchain = attrib()
    token = attrib()
    kbapi_url = attrib()
    tuxapi_url = attrib()
    group = attrib()
    project = attrib()
    environment = attrib(default={})
    targets = attrib(default=[])
    make_variables = attrib(default={})
    kernel_image = attrib(default=None)
    patch_series = attrib(default=None)
    image_sha = attrib(default=None)

    build_data = attrib(default=None)
    build_name = attrib(default=None)
    status = attrib(default={})
    uid = attrib(default=None)
    json = attrib(default=False)
    limit = attrib(default=0)
    no_cache = attrib(default=False)
    is_public = attrib(default=True)
    callback = attrib(default=None)
    callback_headers = attrib(default=None)
    notify_emails = attrib(default=[])

    def __attrs_post_init__(self):
        if isinstance(self.kconfig, str):
            self.kconfig = [self.kconfig]
        self.verify_build_parameters()
        self.client_token = str(uuid.uuid4())

    def __lt__(self, other):
        return (self.target_arch, self.toolchain) < (other.target_arch, other.toolchain)

    def __str__(self):
        git_short_log = self.status.get("git_short_log", "")

        if len(self.kconfig) > 1:
            kconfig = f"{self.kconfig[0]}+{len(self.kconfig)-1}"  # noqa: E226
        else:
            kconfig = self.kconfig[0]
        return "{} {} ({}) with {} @ {}".format(
            git_short_log,
            self.target_arch,
            kconfig,
            self.toolchain,
            self.build_data,
        )

    @staticmethod
    def is_supported_git_url(url):
        """
        Check that the git url provided is valid (namely, that it's not an ssh
        url)
        """
        return re.match(r"^(git://|https?://).*$", url) is not None

    def generate_build_request(self, plan=None):
        """return a build data in a python dict"""
        build_entry = {}
        patch = {}
        build_entry["client_token"] = self.client_token
        build_entry["git_repo"] = self.git_repo
        if self.git_ref:
            build_entry["git_ref"] = self.git_ref
        if self.git_sha:
            build_entry["git_sha"] = self.git_sha
        build_entry["target_arch"] = self.target_arch
        build_entry["toolchain"] = self.toolchain
        build_entry["kconfig"] = self.kconfig
        build_entry["environment"] = dict(self.environment)
        build_entry["targets"] = self.targets
        build_entry["make_variables"] = self.make_variables
        if self.is_public is not None:
            build_entry["is_public"] = self.is_public
        if self.kernel_image:
            build_entry["kernel_image"] = self.kernel_image
        if self.build_name:
            build_entry["build_name"] = self.build_name
        if plan is not None:
            build_entry["plan"] = plan
        if self.image_sha:
            build_entry["image_sha"] = self.image_sha
        if self.no_cache:
            build_entry["no_cache"] = self.no_cache
        if self.patch_series:
            (
                build_entry["kernel_patch_file"],
                kernel_patch,
            ) = handle_patch(self.patch_series)
            patch[build_entry["kernel_patch_file"]] = kernel_patch
        if self.callback is not None:
            build_entry["callback"] = self.callback
        if self.callback_headers is not None:
            build_entry["callback_headers"] = self.callback_headers
        if self.notify_emails:
            build_entry["notify_emails"] = self.notify_emails
        return (build_entry, patch)

    def verify_build_parameters(self):
        """Pre-check the build arguments"""
        try:
            assert self.git_repo, "git_repo is mandatory\n"
            assert self.is_supported_git_url(
                self.git_repo
            ), "git url must be in the form of git:// or http:// or https://\n"
            assert (self.git_ref and not self.git_sha) or (
                self.git_sha and not self.git_ref
            ), "Either a git_ref or a git_sha is required\n"
            assert self.target_arch is not None, "target-arch is mandatory\n"
            assert self.kconfig, "kconfig is mandatory\n"
            assert self.toolchain, "toolchain is mandatory\n"
            assert self.headers is not None, "headers is mandatory\n"
        except AssertionError as exc:
            error(str(exc))

    def build(self, plan=None):
        """Submit the build request"""
        data = {}
        build_entry, patch = self.generate_build_request(plan=plan)
        data["builds"] = [build_entry]
        data["patches"] = patch
        url = self.tuxapi_url + "/v1/groups/{}/projects/{}/builds".format(
            self.group, self.project
        )
        self.status = post_request(url, self.headers, data)[0]
        self.uid = self.status["uid"]
        self.build_data = f"{url}/{self.uid}"

    def get_status(self):
        """Fetches the build status and updates the values inside the build object"""
        url = self.tuxapi_url + "/v1/groups/{}/projects/{}/builds/{}".format(
            self.group, self.project, self.uid
        )
        self.status = get_request(url, self.headers)

    def watch(self, iterator=False):
        """
        Wait for the build to finish. Whenever the state changes, yielding the
        new state).
        """
        waiting_states = {
            "queued": BuildState(
                build=self,
                state="queued",
                message="Queued",
                icon="⏳",
                cli_color="white",
            ),
            "provisioning": BuildState(
                build=self,
                state="provisioning",
                message="Provisioning",
                icon="⚙️ ",
                cli_color="white",
            ),
            "building": BuildState(
                build=self,
                state="building",
                message="Building",
                icon="🚀",
                cli_color="cyan",
            ),
            "running": BuildState(
                build=self,
                state="running",
                message="Running",
                icon="🚀",
                cli_color="cyan",
            ),
        }
        previous_state = None
        while True:
            self.get_status()
            state = self.status["state"]
            retry = self.status.get("retry", 0)
            if state != previous_state:
                if retry:
                    message = self.status.get("status_message", "infrastructure error")
                    yield BuildState(
                        build=self,
                        state=self.status["tuxbuild_status"],
                        message=message + f" - retrying (attempt {retry})",
                        icon="🔧",
                        cli_color="yellow",
                    )
                elif state in waiting_states:
                    yield waiting_states[state]
                elif state == "finished":
                    break
                else:
                    # unknown state
                    yield BuildState(
                        build=self,
                        state=state,
                        message=self.status.get("status_message", state),
                        icon="🎰",
                        cli_color="yellow",
                    )
            elif iterator:
                yield

            if not iterator:
                delay = random.randrange(delay_status_update)
                time.sleep(delay)
            previous_state = state

        errors = 0
        warnings = 0
        state = self.status["tuxbuild_status"]
        status = self.status["build_status"]

        if status == "pass":
            warnings = self.status["warnings_count"]
            if warnings == 0:
                icon = "🎉"
                message = "Pass"
                cli_color = "green"
            else:
                icon = "👾"
                cli_color = "yellow"
                if warnings == 1:
                    message = "Pass (1 warning)"
                else:
                    message = "Pass ({} warnings)".format(warnings)
        elif status == "fail":
            icon = "👹"
            cli_color = "bright_red"
            errors = self.status["errors_count"]
            if errors == 1:
                message = "Fail (1 error)"
            else:
                message = "Fail ({} errors)".format(errors)
            error_message = self.status.get("status_message")
            if error_message:
                message += f" with status message '{error_message}'"
        elif status == "canceled":
            icon = "⚠️ "
            cli_color = "white"
            message = "Canceled"
        elif status == "unknown":
            icon = "🧐"
            cli_color = "purple"
            message = "Unknown"
        else:
            icon = "🔧"
            cli_color = "bright_red"
            message = self.status["status_message"]

        finished = BuildState(
            build=self,
            state=state,
            status=status,
            final=True,
            message=message,
            icon=icon,
            cli_color=cli_color,
            warnings=warnings,
            errors=errors,
        )
        yield finished

    def wait(self):
        state = None
        for s in self.watch():
            state = s
        return state

    def _get_field(self, field):
        """Retrieve an individual field from status.json"""
        self.get_status()
        return self.status.get(field, None)

    @property
    def warnings_count(self):
        """Get the warnings_count for the build"""
        return int(self._get_field("warnings_count"))

    @property
    def errors_count(self):
        """Get the errors_count for the build"""
        return int(self._get_field("errors_count"))

    @property
    def tuxbuild_status(self):
        """Get the tuxbuild_status for the build"""
        return self._get_field("state")

    @property
    def build_status(self):
        """Get the build_status for the build"""
        return self._get_field("result")

    @property
    def status_message(self):
        """Get the build_status for the build"""
        return self._get_field("status_message")


class Plan(HeadersMixin):
    def __init__(self, config, **kwargs):
        self.config = config
        self.token = kwargs["token"]
        self.tuxapi_url = kwargs["tuxapi_url"]
        self.project = kwargs["project"]
        self.group = kwargs["group"]
        self.lava_test_plans_project = kwargs["lava_test_plans_project"]
        self.lab = kwargs["lab"]
        self.args = kwargs
        self.parameters = kwargs.get("parameters", [])
        self.plan = kwargs.get("plan", None)
        self.is_public = kwargs.get("is_public", True)  # plan public or private
        self.plan_callback = kwargs.get("plan_callback")
        self.plan_callback_headers = kwargs.get("plan_callback_headers")
        self.notify_emails = kwargs.get("notify_emails", [])
        self.builds = []
        self.tests = []
        self.status = {}
        self.url = self.tuxapi_url + "/v1/groups/{}/projects/{}".format(
            self.group, self.project
        )
        self.results = {"builds": {}, "tests": {}}
        # setting respective plan type class obj
        if self.config and hasattr(self.config, "plan_type"):
            self.plan_type = self.config.plan_type
        else:
            # setting default plan as BuildPlan ( kernel )
            self.plan_type = tuxsuite.BuildPlan()

    def submit(self):
        builds = []
        tests = []
        sanity_tests = []
        builds_status = {}
        tests_status = {}

        # Create the plan
        self.plan = post_request(
            f"{self.url}/plans",
            self.headers,
            {
                "name": self.config.name,
                "description": self.config.description,
                "is_public": self.is_public,
                "plan_callback": self.plan_callback,
                "plan_callback_headers": self.plan_callback_headers,
                "count": self.plan_type.count(self),
                "plan_file": self.config.plan_file,
                "notify_emails": self.notify_emails,
            },
        )["uid"]

        # calling respective plan type class to create builds
        self.plan_type.create_builds(self, builds)

        # create sanity tests
        for build, cfg in zip(builds, self.config.plan):
            if cfg.get("sanity_test"):
                sanity_tests.append(
                    self.get_test_obj(build if build else None, cfg["sanity_test"])
                )
            else:
                sanity_tests.append(None)

        # send sanity_test to tuxapi
        filtered_sanity_tests = [t for t in sanity_tests if t]
        if filtered_sanity_tests:
            ret = post_request(
                f"{self.url}/tests",
                self.headers,
                [
                    t.generate_test_request(plan=self.plan)
                    for t in filtered_sanity_tests
                ],
            )
            for test, data in zip(filtered_sanity_tests, ret):
                test.uid = data["uid"]
                test.status = data
                self.tests.append(test)

        # Create the tests
        for build, cfg, sanity_test in zip(builds, self.config.plan, sanity_tests):
            if build:
                for test in cfg["tests"]:
                    tests.append(
                        self.get_test_obj(
                            build,
                            test,
                            f"TEST#{sanity_test.uid}" if sanity_test else None,
                        )
                    )
                self.builds.append(build)
            else:
                for test in cfg["tests"]:
                    tests.append(
                        self.get_test_obj(
                            None,
                            test,
                            f"TEST#{sanity_test.uid}" if sanity_test else None,
                        )
                    )

        if tests:
            ret = []
            # submit in batches of 500 to prevent tuxapi lambda time out
            for i in range(0, len(tests), 500):
                ret += post_request(
                    f"{self.url}/tests",
                    self.headers,
                    [
                        t.generate_test_request(plan=self.plan)
                        for t in tests[i : i + 500]
                    ],
                )
            for test, data in zip(tests, ret):
                test.uid = data["uid"]
                test.status = data
                self.tests.append(test)

        # Populate the status with builds and tests after submission
        for build in self.builds:
            builds_status.update({build.uid: build.status})
        for test in self.tests:
            tests_status.update({test.uid: test.status})
        self.status = {"builds": builds_status, "tests": tests_status}

    def get_test_obj(self, build, test, wait_for=None):
        new_overlays = []
        for overlay in test.get("overlay", []):
            if isinstance(overlay, list):
                ovl_len = len(overlay)
                if ovl_len == 1:
                    new_overlays.append([overlay[0], "/"])
                elif ovl_len == 2:
                    new_overlays.append([overlay[0], overlay[1]])
                if ovl_len > 2:
                    raise Exception(
                        f"overlay can't have more than 2 parameters: {overlay}"
                    )
            else:
                new_overlays.append([overlay, "/"])
        test["overlay"] = new_overlays
        # process additional parameters if available in cmdargs
        test["parameters"] = test.get("parameters", {})
        for p in self.parameters:
            key, val = p
            if key not in test["parameters"]:
                test["parameters"][key] = val
        if build:
            return Test(
                token=self.token,
                kbapi_url="",
                tuxapi_url=self.tuxapi_url,
                group=self.group,
                project=self.project,
                lava_test_plans_project=test.get("lava_test_plans_project")
                or self.lava_test_plans_project,
                lab=test.get("lab") or self.lab,
                bios=test.get("bios"),
                boot_args=test.get("boot_args"),
                device=test["device"],
                dtb=test.get("dtb"),
                parameters=test.get("parameters", {}),
                rootfs=test.get("rootfs"),
                tests=test.get("tests", []),
                test_name=test.get("test_name", None),
                overlays=test.get("overlay", []),
                timeouts=test.get("timeouts"),
                callback=test.get("callback") or self.args.get("callback"),
                callback_headers=test.get("callback_header")
                or self.args.get("callback_headers"),
                wait_for=(
                    f"{self.plan_type.name}#{build.uid}"
                    if wait_for is None
                    else wait_for
                ),
                commands=test.get("commands", []),
                qemu_image=test.get("qemu_image"),
                shared=test.get("shared"),
                host=test.get("host"),
                tuxbuild=test.get("tuxbuild"),
                notify_emails=test.get("notify_emails"),
            )
        else:
            return Test(
                token=self.token,
                kbapi_url="",
                tuxapi_url=self.tuxapi_url,
                group=self.group,
                project=self.project,
                lava_test_plans_project=test.get("lava_test_plans_project")
                or self.lava_test_plans_project,
                lab=test.get("lab") or self.lab,
                ap_romfw=test.get("ap_romfw"),
                bios=test.get("bios"),
                boot_args=test.get("boot_args"),
                device=test["device"],
                dtb=test.get("dtb"),
                fip=test.get("fip"),
                kernel=test.get("kernel"),
                mcp_fw=test.get("mcp_fw"),
                mcp_romfw=test.get("mcp_romfw"),
                modules=test.get("modules"),
                overlays=test.get("overlay", []),
                parameters=test.get("parameters", {}),
                rootfs=test.get("rootfs"),
                scp_fw=test.get("scp_fw"),
                scp_romfw=test.get("scp_romfw"),
                tests=test.get("tests", []),
                test_name=test.get("test_name", None),
                timeouts=test.get("timeouts"),
                callback=test.get("callback") or self.args.get("callback"),
                callback_headers=test.get("callback_header")
                or self.args.get("callback_headers"),
                commands=test.get("commands", []),
                qemu_image=test.get("qemu_image"),
                shared=test.get("shared"),
                host=test.get("host"),
                tuxbuild=test.get("tuxbuild"),
                notify_emails=test.get("notify_emails"),
                wait_for=wait_for,
            )

    def load_kernel_builds(self, b):
        git_ref = b.get("git_ref")
        git_sha = b.get("git_sha")
        if git_ref:
            git_sha = None
        build = Build(
            git_repo=b["git_repo"],
            git_ref=git_ref,
            git_sha=git_sha,
            target_arch=b["target_arch"],
            kconfig=b["kconfig"],
            toolchain=b["toolchain"],
            token=self.token,
            kbapi_url=None,
            tuxapi_url=self.tuxapi_url,
            group=self.group,
            project=b["project"],
            environment=b.get("environment"),
            targets=b.get("targets"),
            make_variables=b.get("make_variables"),
            kernel_image=b.get("kernel_image"),
            build_data=b.get("build_data"),
            build_name=b.get("build_name"),
            status=b,
            uid=b["uid"],
        )
        return build

    def load_bake_builds(self, b):
        build_definition = {
            key: val
            for key, val in b.items()
            if key
            in [
                "envsetup",
                "distro",
                "machine",
                "sources",
                "environment",
                "artifacts",
                "local_conf",
                "bblayers_conf",
                "manifest",
                "container",
                "targets",
                "target",
            ]
        }
        oebuild = Bitbake(
            token=self.token,
            kbapi_url=None,
            tuxapi_url=self.tuxapi_url,
            group=self.group,
            project=b["project"],
            build_data=b.get("build_data"),
            status=b,
            uid=b["uid"],
            data=build_definition,
        )
        return oebuild

    def load(self, data):
        # builds --> kernel or bake
        for uid, b in data["builds"].items():
            if "build_name" in b:
                build = self.load_kernel_builds(b)
                self.builds.append(build)
            elif "sources" in b:
                oebuild = self.load_bake_builds(b)
                self.builds.append(oebuild)

        # tests
        for uid, t in data["tests"].items():
            test = Test(
                device=t["device"],
                token=self.token,
                kbapi_url=None,
                tuxapi_url=self.tuxapi_url,
                group=self.group,
                project=t["project"],
                lava_test_plans_project=self.lava_test_plans_project,
                lab=self.lab,
                status=t,
                tests=t["tests"],
                uid=t["uid"],
            )
            self.tests.append(test)

    def get_plan(self):
        builds = {}
        tests = {}
        first = True
        start_builds = start_oebuilds = start_tests = None
        while (
            first
            or start_builds is not None
            or start_tests is not None
            or start_oebuilds is not None
        ):
            ret = get_request(
                f"{self.url}/plans/{self.plan}",
                headers=self.headers,
                params={
                    "start_builds": start_builds,
                    "start_tests": start_tests,
                    "start_oebuilds": start_oebuilds,
                },
            )
            if first or start_builds is not None:
                builds.update({b["uid"]: b for b in ret["builds"]["results"]})
                start_builds = ret["builds"]["next"]
            if first or start_oebuilds is not None:
                builds.update({b["uid"]: b for b in ret["oebuilds"]["results"]})
                start_oebuilds = ret["oebuilds"]["next"]
            if first or start_tests is not None:
                tests.update({t["uid"]: t for t in ret["tests"]["results"]})
                start_tests = ret["tests"]["next"]

            first = False

        self.status = {"builds": builds, "tests": tests}
        return self.status

    def _tests_wait_for(self, uid):
        return [
            t
            for t in self.tests
            if t.status["waiting_for"] and t.status["waiting_for"].split("#")[1] == uid
        ]

    def filter_builds(self, f):
        return sorted([b for b in self.builds if f(self, b)])

    def filter_tests(self, f):
        return sorted([t for t in self.tests if f(self, t)])

    def passing(self):
        def __filter(plan, build):
            return (
                build.status["result"] == "pass"
                and build.status.get("warnings_count", 0) == 0
            ) and (
                all(
                    [
                        t.status["result"] == "pass"
                        for t in plan._tests_wait_for(build.uid)
                    ]
                )
            )

        return self.filter_builds(__filter)

    def warning(self):
        def __filter(plan, build):
            return (
                build.status["result"] == "pass"
                and build.status.get("warnings_count", 0) != 0
            ) and (
                all(
                    [
                        t.status["result"] == "pass"
                        for t in self._tests_wait_for(build.uid)
                    ]
                )
            )

        return self.filter_builds(__filter)

    def failing(self):
        def __filter(plan, build):
            return build.status["result"] == "fail" or any(
                [t.status["result"] == "fail" for t in self._tests_wait_for(build.uid)]
            )

        return self.filter_builds(__filter)

    def errors(self):
        def __filter(plan, build):
            return build.status["result"] == "error" or any(
                [t.status["result"] == "error" for t in self._tests_wait_for(build.uid)]
            )

        return self.filter_builds(__filter)

    def canceled(self):
        def __filter(plan, build):
            return build.status["result"] == "canceled"

        return self.filter_builds(__filter)

    def unknown(self):
        def __filter(plan, build):
            return build.status["result"] == "unknown"

        return self.filter_builds(__filter)

    def watch(self):
        n_builds = len(self.builds)
        n_tests = len(self.tests)

        while True:
            plan = self.get_plan()
            for build in [b for b in self.builds if b.uid in plan["builds"]]:
                if build.uid not in self.results["builds"]:
                    build.status = plan["builds"][build.uid]
                    if not hasattr(build, "ite"):
                        build.get_status = lambda: None
                        build.ite = build.watch(iterator=True)
                    state = next(build.ite)
                    if state is not None:
                        yield state
                        if state.final:
                            self.results["builds"][build.uid] = state
            for test in [t for t in self.tests if t.uid in plan["tests"]]:
                if test.uid not in self.results["tests"]:
                    test.get = lambda: plan["tests"][test.uid]
                    if not hasattr(test, "ite"):
                        test.ite = test.watch(iterator=True)
                    state = next(test.ite)
                    if state is not None:
                        yield state
                        if state.final:
                            self.results["tests"][test.uid] = state

            nr_builds = len(self.results["builds"])
            nr_tests = len(self.results["tests"])
            if nr_builds == n_builds and nr_tests == n_tests:
                break
            time.sleep(random.randrange(delay_status_update))

    def wait(self):
        states = []
        for s in self.watch():
            if s.final:
                states.append(s)
        return states

    @property
    def build_status_list(self):
        """Return a list of build status dictionaries"""
        return [b.status for b in self.builds]


@attrs(kw_only=True)
class Test(HeadersMixin):
    token = attrib()
    kbapi_url = attrib()
    tuxapi_url = attrib()
    group = attrib()
    project = attrib()
    lava_test_plans_project = attrib()
    lab = attrib()
    device = attrib()

    ap_romfw = attrib(default=None)
    boot_args = attrib(default=None)
    bios = attrib(default=None)
    dtb = attrib(default=None)
    fip = attrib(default=None)
    job_definition = attrib(default=None)
    kernel = attrib(default=None)
    mcp_fw = attrib(default=None)
    mcp_romfw = attrib(default=None)
    modules = attrib(default=None)
    overlays = attrib(default=[])
    parameters = attrib(default=[])
    rootfs = attrib(default=None)
    scp_fw = attrib(default=None)
    scp_romfw = attrib(default=None)
    tests = attrib(default=[])
    test_name = attrib(default=None)
    timeouts = attrib(default=[])
    callback = attrib(default=None)
    callback_headers = attrib(default=None)
    commands = attrib(default=[])
    qemu_image = attrib(default=None)
    shared = attrib(default=False)
    host = attrib(default="x86_64")
    tuxbuild = attrib(default=None)
    notify_emails = attrib(default=[])

    uid = attrib(default=None)
    wait_for = attrib(default=None)
    status = attrib(default={})
    url = attrib(default=None)
    is_public = attrib(default=True)

    def __str__(self):
        tests = "[" + ", ".join(["boot"] + self.tests) + "]"
        self.url = self.tuxapi_url + "/v1/groups/{}/projects/{}/tests/{}".format(
            self.group, self.project, self.uid
        )
        return "{} {} @ {}".format(tests, self.device, self.url)

    def generate_test_request(self, plan=None):
        data = {
            "ap_romfw": self.ap_romfw,
            "bios": self.bios,
            "device": self.device,
            "dtb": self.dtb,
            "fip": self.fip,
            "kernel": self.kernel,
            "mcp_fw": self.mcp_fw,
            "mcp_romfw": self.mcp_romfw,
            "parameters": self.parameters,
            "rootfs": self.rootfs,
            "scp_fw": self.scp_fw,
            "scp_romfw": self.scp_romfw,
            "lava_test_plans_project": self.lava_test_plans_project,
            "lab": self.lab,
            "is_public": self.is_public,
        }
        if self.modules:
            data["modules"] = self.modules
        if self.overlays:
            data["overlays"] = self.overlays
        if self.tests:
            data["tests"] = self.tests
        if self.test_name:
            data["test_name"] = self.test_name
        if self.timeouts:
            data["timeouts"] = self.timeouts
        if self.boot_args:
            data["boot_args"] = self.boot_args
        if self.wait_for:
            data["waiting_for"] = self.wait_for
        if self.callback:
            data["callback"] = self.callback
        if self.callback_headers:
            data["callback_headers"] = self.callback_headers
        if self.commands:
            data["commands"] = self.commands
        if self.qemu_image:
            data["qemu_image"] = self.qemu_image
        if self.shared:
            data["shared"] = self.shared
        if self.host:
            data["host"] = self.host
        if self.tuxbuild:
            data["tuxbuild"] = self.tuxbuild
        if self.notify_emails:
            data["notify_emails"] = self.notify_emails
        if plan is not None:
            data["plan"] = plan

        # lava job definition file
        if self.job_definition:
            (data["job_definition"], job_definition_content) = handle_attachment(
                self.job_definition, file_type="yaml"
            )
            data["attachments"] = {data["job_definition"]: job_definition_content}
        return data

    def test(self, plan=None):
        url = self.tuxapi_url + "/v1/groups/{}/projects/{}/tests".format(
            self.group, self.project
        )
        data = self.generate_test_request(plan=plan)
        self.status = post_request(url, self.headers, data)
        self.uid = self.status["uid"]
        self.url = url + "/{}".format(self.uid)

    def get(self):
        self.status = get_request(self.url, self.headers)
        return self.status

    def watch(self, iterator=False):
        """
        Wait for the test to finish. Whenever the state changes, yielding the
        new state).
        """
        waiting_states = {
            "waiting": BuildState(
                build=self,
                state="waiting",
                message="Waiting",
                icon="⏳",
                cli_color="white",
            ),
            "provisioning": BuildState(
                build=self,
                state="provisioning",
                message="Provisioning",
                icon="⚙️ ",
                cli_color="white",
            ),
            "running": BuildState(
                build=self,
                state="running",
                message="Running",
                icon="🚀",
                cli_color="cyan",
            ),
        }
        previous_state = None
        while True:
            self.status = self.get()
            state = self.status["state"]
            if state != previous_state:
                if state in waiting_states:
                    yield waiting_states[state]
                elif state == "finished":
                    break
                else:
                    assert 0
            elif iterator:
                yield

            if not iterator:
                delay = random.randrange(delay_status_update)
                time.sleep(delay)
            previous_state = state

        errors = 0
        result = self.status["result"]
        if result == "pass":
            icon = "🎉"
            message = "Pass"
            cli_color = "green"
        elif result == "fail":
            icon = "👹"
            cli_color = "bright_red"
            errors = [
                name
                for name in self.status["results"]
                if self.status["results"][name] == "fail"
            ]
            message = "Fail ({})".format(", ".join(errors))
            errors = len(errors)
        elif result == "canceled":
            icon = "⚠️ "
            cli_color = "white"
            message = "Canceled"
        elif result == "unknown":
            icon = "🧐"
            cli_color = "purple"
            message = "Unknown"
        else:
            icon = "🔧"
            cli_color = "bright_red"
            message = self.status.get("status_message", "TuxTest error")

        finished = BuildState(
            build=self,
            state=state,
            status=result,
            final=True,
            message=message,
            icon=icon,
            cli_color=cli_color,
            errors=errors,
        )
        yield finished

    def wait(self):
        state = None
        for s in self.watch():
            state = s
        return state


@attrs(kw_only=True)
class Results(HeadersMixin):
    token = attrib()
    kbapi_url = attrib()
    tuxapi_url = attrib()
    group = attrib()
    project = attrib()
    lava_test_plans_project = attrib()
    lab = attrib()
    uid = attrib(default=None)

    def get_build(self):
        url = self.tuxapi_url + "/v1/groups/{}/projects/{}/builds/{}".format(
            self.group, self.project, self.uid
        )
        result = get_request(url, self.headers)
        return (result, url)

    def get_test(self):
        url = self.tuxapi_url + "/v1/groups/{}/projects/{}/tests/{}".format(
            self.group, self.project, self.uid
        )
        result = get_request(url, self.headers)
        return (result, url)

    def get_oebuild(self):
        url = self.tuxapi_url + "/v1/groups/{}/projects/{}/oebuilds/{}".format(
            self.group, self.project, self.uid
        )
        result = get_request(url, self.headers)
        return (result, url)

    def get_plan(self):
        plan = Plan(
            None,
            token=self.token,
            tuxapi_url=self.tuxapi_url,
            project=self.project,
            group=self.group,
            plan=self.uid,
            lava_test_plans_project=self.lava_test_plans_project,
            lab=self.lab,
        )
        # TODO: Return the test url as part of the test result in tuxapi
        tuxapi_url = plan.url
        return (plan.get_plan(), tuxapi_url)

    def get_all(self):
        all_results = {}
        url = self.tuxapi_url + "/v1/groups/{}/projects/{}".format(
            self.group, self.project
        )
        # availables builds and tests
        result_types = ["builds", "tests", "plans", "oebuilds"]
        for res_type in result_types:
            type_url = url + f"/{res_type}"
            all_results[res_type] = get_request(type_url, self.headers)

        return (all_results, url)


@attrs(kw_only=True, order=False)
class Bitbake(HeadersMixin):
    token = attrib()
    tuxapi_url = attrib()
    kbapi_url = attrib()
    status = attrib(default={})
    uid = attrib(default=None)
    group = attrib()
    project = attrib()
    data = attrib(default={})
    build_definition = attrib(default={})
    build_data = attrib(default=None)
    # manifest = attrib(default=None)

    @attrs(kw_only=True, order=False)
    class BuildDefinition:
        target = attrib(default=None)
        targets = attrib(default=None)
        envsetup = attrib(default=None)
        distro = attrib(default=None)
        machine = attrib(default=None)
        sources = attrib()
        artifacts = attrib(default=[])
        environment = attrib(default={})
        local_conf = attrib(default=[])
        bblayers_conf = attrib(default=[])
        container = attrib(default="ubuntu-20.04")
        manifest_file = attrib(default=None)
        name = attrib(default="")
        no_cache = attrib(default=False)
        extraconfigs = attrib(default=[])
        pinned_manifest = attrib(default=None)
        kas_override = attrib(default=None)
        is_public = attrib(default=True)
        callback = attrib(default=None)
        callback_headers = attrib(default=None)
        notify_emails = attrib(default=[])

    def __attrs_post_init__(self):
        self.build_definition = self.BuildDefinition(**(self.data))
        # TODO: Temp legacy target fixes, to be removed after we deprecate target
        try:
            if (
                self.build_definition.targets is None
                and self.build_definition.target is not None
            ):
                if not isinstance(self.build_definition.target, str):
                    raise Exception(
                        f"Unexpected argument for target: {self.build_definition.target}, expected string"
                    )
                else:
                    self.build_definition.targets = [self.build_definition.target]
        except Exception as e:
            sys.stderr.write(f"{str(e)}\n")
            sys.exit(1)

    # Currently of no use but needed for Plan filters(passing, warnings, failings etc.)
    def __lt__(self, other):
        pass

    def __str__(self):
        return "{} with {} {} for {}: {} ".format(
            self.build_definition.sources,
            self.build_definition.distro,
            self.build_definition.machine,
            self.build_definition.targets,
            self.build_data,
        )

    def generate_build_request(self, plan=None):
        """return a build data in a python dict"""
        manifests = {}
        build_data = self.build_definition.__dict__
        if plan is None:
            # local manifest
            if self.build_definition.manifest_file:
                (build_data["manifest_file"], manifest) = handle_attachment(
                    self.build_definition.manifest_file
                )
                manifests[build_data["manifest_file"]] = manifest
            # pinned manifest
            if self.build_definition.pinned_manifest:
                (build_data["pinned_manifest"], manifest) = handle_attachment(
                    self.build_definition.pinned_manifest
                )
                manifests[build_data["pinned_manifest"]] = manifest
            # kas override
            if self.build_definition.kas_override:
                (build_data["kas_override"], override_content) = handle_attachment(
                    self.build_definition.kas_override, file_type="yaml"
                )
                manifests[build_data["kas_override"]] = override_content
        else:
            # we are separately handling manifest for plan
            build_data["plan"] = plan
        return (build_data, manifests)

    def build(self, plan=None):
        """Submit the build request"""
        # Here manifest can either be local or pinned, based upon that will be assigning manifest in data
        data, manifest = self.generate_build_request(plan=plan)
        data["manifests"] = manifest

        url = self.tuxapi_url + "/v1/groups/{}/projects/{}/oebuilds".format(
            self.group, self.project
        )
        self.status = post_request(url, self.headers, data)
        self.uid = self.status["uid"]
        self.build_data = f"{url}/{self.uid}"

    def get_status(self):
        """Fetches the build status and updates the values inside the build object"""
        url = self.tuxapi_url + "/v1/groups/{}/projects/{}/oebuilds/{}".format(
            self.group, self.project, self.uid
        )
        self.status = get_request(url, self.headers)

    def watch(self, iterator=False):
        """
        Wait for the build to finish. Whenever the state changes, yielding the
        new state).
        """
        waiting_states = {
            "provisioning": BuildState(
                build=self,
                state="provisioning",
                message="Provisioning",
                icon="⚙️ ",
                cli_color="white",
            ),
            "running": BuildState(
                build=self,
                state="running",
                message="Running",
                icon="🚀",
                cli_color="cyan",
            ),
        }
        previous_state = None
        while True:
            self.get_status()
            state = self.status["state"]
            if state != previous_state:
                if state in waiting_states:
                    yield waiting_states[state]
                elif state == "finished":
                    break
            elif iterator:
                yield

            if not iterator:
                delay = random.randrange(delay_status_update)
                time.sleep(delay)
            previous_state = state

        errors = 0
        warnings = 0
        state = self.status["state"]
        status = self.status["result"]

        if status == "pass":
            warnings = self.status["warnings_count"]
            if warnings == 0:
                icon = "🎉"
                message = "Pass"
                cli_color = "green"
            else:
                icon = "👾"
                cli_color = "yellow"
                if warnings == 1:
                    message = "Pass (1 warning)"
                else:
                    message = "Pass ({} warnings)".format(warnings)
        elif status == "fail":
            icon = "👹"
            cli_color = "bright_red"
            errors = self.status["errors_count"]
            message = "Fail (1 error)"
            error_message = self.status.get("status_message")
            if error_message:
                message += f" with status message '{error_message}'"
        elif status == "canceled":
            icon = "⚠️ "
            cli_color = "white"
            message = "Canceled"
        elif status == "unknown":
            icon = "🧐"
            cli_color = "purple"
            message = "Unknown"
        else:
            icon = "🔧"
            cli_color = "bright_red"
            message = self.status["status_message"]

        finished = BuildState(
            build=self,
            state=state,
            status=status,
            final=True,
            message=message,
            icon=icon,
            cli_color=cli_color,
            warnings=warnings,
            errors=errors,
        )
        yield finished

    def wait(self):
        state = None
        for s in self.watch():
            state = s
        return state

    def _get_field(self, field):
        """Retrieve an individual field from status.json"""
        self.get_status()
        return self.status.get(field, None)

    @property
    def warnings_count(self):
        """Get the warnings_count for the build"""
        return int(self._get_field("warnings_count"))

    @property
    def errors_count(self):
        """Get the errors_count for the build"""
        return int(self._get_field("errors_count"))

    @property
    def build_status(self):
        """Get the build_status for the build"""
        return self._get_field("result")

    @property
    def status_message(self):
        """Get the build_status for the build"""
        return self._get_field("status_message")
