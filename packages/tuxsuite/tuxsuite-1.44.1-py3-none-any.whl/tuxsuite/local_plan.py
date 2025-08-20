# -*- coding: utf-8 -*-

from attr import attrs, attrib
import json
import os
from pathlib import Path
import subprocess
import sys

from tuxsuite import xdg
from tuxsuite.exceptions import TuxSuiteError


def colorize(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"


def get_new_output_dir(output_dir):
    base = xdg.get_cache_dir() / "plan"
    if output_dir:
        base = Path(f"{os.path.abspath(output_dir)}/plan")
    base.mkdir(parents=True, exist_ok=True)
    existing = [int(f.name) for f in base.glob("[0-9]*")]
    if existing:
        new = max(existing) + 1
    else:
        new = 1
    while True:
        new_dir = base / str(new)
        try:
            new_dir.mkdir()
            break
        except FileExistsError:
            new += 1
    return new_dir


def check_container(func):
    # checks for pre-built fvp containers
    def wrapper(self, *args, **kwargs):
        if self.device == "fvp-aemva" or self.device.startswith("fvp-morello"):
            image = (
                "fvp:aemva-11.24.11"
                if self.device == "fvp-aemva"
                else "fvp:morello-0.11.34"
            )
            cmd = f"{self.runtime} image inspect {image}".split()
            try:
                subprocess.check_call(
                    cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            except subprocess.CalledProcessError:
                doc_url = "https://tuxrun.org/run-fvp/#preparing-the-environment"
                print(
                    f"FVP containers not available!\nPlease prepare the environment: {doc_url}"
                )
                sys.exit(1)

        return func(self, *args, **kwargs)

    return wrapper


class LocalPlan:
    def __init__(self, cmdargs, plan_cfg):
        self.__ret_code__ = None

        self.args = cmdargs
        self.plan_cfg = plan_cfg
        self.builds = []
        self.tests = []
        self.runtime = cmdargs.runtime
        self.output_dir = get_new_output_dir(cmdargs.output_dir)
        self.build_args = {
            "tree": cmdargs.tree,
            "runtime": cmdargs.runtime,
            "wrapper": cmdargs.wrapper,
        }
        self.__process_plan__()

    @classmethod
    def check_tools(cls, runtime):
        for tool in ["tuxmake", "tuxrun"]:
            try:
                cmd = f"python3 -m {tool} --version".split()
                subprocess.check_call(cmd, stdout=subprocess.DEVNULL)
            except FileNotFoundError:
                sys.stderr.write(
                    f"Package '{tool}' not installed, but can be installed with:\npip3 install {tool}\n"
                )
                sys.exit(1)
        try:
            subprocess.check_call([runtime, "--version"], stdout=subprocess.DEVNULL)
        except FileNotFoundError:
            sys.stderr.write(f"Runtime not installed: {runtime}\n")
            sys.exit(1)

    def __process_plan__(self):
        for idx, item in enumerate(self.plan_cfg.plan, 1):
            if item["build"] is not None:
                build_obj = LocalBuild(
                    **item["build"],
                    **self.build_args,
                    output_dir=f"{self.output_dir}/build_{idx}",
                )
                tests = []
                for t_idx, test in enumerate(item["tests"], 1):
                    tests.append(
                        LocalTest(
                            **test,
                            output_dir=f"{build_obj.output_dir}/tests/{t_idx}",
                            runtime=self.runtime,
                        )
                    )
                build_obj.dependent_tests = tests
                self.builds.append(build_obj)
            else:
                for t_idx, test in enumerate(item["tests"], 1):
                    self.tests.append(
                        LocalTest(
                            **test,
                            output_dir=f"{self.output_dir}/tests_{idx}/{t_idx}",
                            runtime=self.runtime,
                        )
                    )

    def submit(self):
        if self.builds or self.tests:
            print("==> Submitting Local Plan\n")
            for build in self.builds:
                build.submit()
                build.submit_tests()  # build dependent tests

            # standalone tests
            for test in self.tests:
                test.submit()
        else:
            print("No jobs to submit. Exiting.")

    def summary(self):
        if self.builds or self.tests:
            print("\nPlan summary: ")
            for build in self.builds:
                build.summary()
            for test in self.tests:
                test.summary()
            print(f"\nOutput directory: {self.output_dir}\n")

    @property
    def ret_code(self):
        if self.__ret_code__ is None:
            for b in self.builds:
                if b.result != "PASS" or any(
                    [t.result != "PASS" for t in b.dependent_tests]
                ):
                    self.__ret_code__ = 1
                    return self.__ret_code__
            for t in self.tests:
                if t.result != "PASS":
                    self.__ret_code__ = 1
                    return self.__ret_code__
            self.__ret_code__ = 0
        return self.__ret_code__


@attrs(kw_only=True, order=False)
class LocalBuild:
    tree = attrib()
    target_arch = attrib()
    kconfig = attrib()
    toolchain = attrib()
    environment = attrib(default={})
    targets = attrib(default=[])
    make_variables = attrib(default={})
    kernel_image = attrib(default=None)
    patch_series = attrib(default=None)
    image_sha = attrib(default=None)
    build_name = attrib(default=None)

    # helper attributes
    runtime = attrib(default="podman")
    wrapper = attrib(default="none")
    dependent_tests = attrib(default=[])
    metadata = attrib(default={})
    result = attrib(default="UNKNOWN")
    output_dir = attrib(default=None)

    def __str__(self) -> str:
        return "{} with {} @ {}".format(
            self.target_arch,
            self.kconfig,
            self.toolchain,
        )

    def get_cmd(self) -> list:
        cmd = (
            f"python3 -m tuxmake --runtime {self.runtime} -C {self.tree} --wrapper {self.wrapper} "
            f"--target-arch {self.target_arch} --toolchain {self.toolchain} --output-dir {self.output_dir}".split()
        )
        if self.patch_series is not None:
            raise TuxSuiteError("Patch series not supported for local plan execution")
        if self.kconfig:
            if isinstance(self.kconfig, str):
                cmd.extend(["--kconfig", self.kconfig])
            elif isinstance(self.kconfig, list):
                cmd.extend(["--kconfig", self.kconfig[0]])
                for config in self.kconfig[1:]:
                    cmd.extend(["--kconfig-add", config])

        for k, v in self.environment.items():
            cmd.extend(["-e", f"{k}={v}"])

        for k, v in self.make_variables.items():
            if v:
                cmd.append(f"{k}={v}")

        if self.kernel_image:
            cmd.extend(["--kernel-image", self.kernel_image])

        cmd.extend(self.targets)

        return cmd

    def submit(self):
        print(f"🚀 Building: {self}\n")
        cmd = self.get_cmd()
        ret = subprocess.call(cmd)
        if ret == 1:
            sys.exit(1)
        else:
            metadata_json = f"{self.output_dir}/metadata.json"
            if os.path.exists(metadata_json):
                with open(metadata_json, "r") as m_f:
                    metadata = json.load(m_f)
                    self.metadata = metadata
            self.result = self.metadata.get("results", {}).get("status", "UNKNOWN")
            self.format_result()

    def submit_tests(self):
        if self.result == "PASS":
            # extract dtbs.tar.xz if present
            if Path(f"{self.output_dir}/dtbs.tar.xz").exists():
                cmd = [
                    "tar",
                    "xaf",
                    f"{self.output_dir}/dtbs.tar.xz",
                    "-C",
                    self.output_dir,
                ]
                subprocess.call(cmd)

            # submit build dependent tests
            for test in self.dependent_tests:
                test.submit(build_dir=self.output_dir)
        elif self.result == "FAIL":
            print("👹 Build failed, skipping tests!!")
        else:
            print("🔧 Error: Skipping build/tests.")

    def format_result(self):
        icon, code = "🧐", 91
        if self.result == "PASS":
            icon, code = "🎉", 92
        elif self.result == "FAIL":
            icon, code = "👹", 91

        print(f"{icon} {colorize(self.result, code)}: {self}\n")

    def summary(self, level=0):
        indentation = "    " * level
        icon, code = "🧐", 91
        if self.result == "PASS":
            icon, code = "✔", 92
        elif self.result == "FAIL":
            icon, code = "✘", 91
        color = colorize(f"{icon} {self.result}", code)
        print(
            f"{indentation}└── Build: {self.toolchain} @ {self.target_arch}: {color}\033[0m"
        )
        for test in self.dependent_tests:
            test.summary(level + 1)


@attrs(kw_only=True, order=False)
class LocalTest:
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
    overlay = attrib(default=[])
    parameters = attrib(default={})
    rootfs = attrib(default=None)
    scp_fw = attrib(default=None)
    scp_romfw = attrib(default=None)
    tests = attrib(default=[])
    test_name = attrib(default=None)
    timeouts = attrib(default=[])
    commands = attrib(default=[])
    qemu_image = attrib(default=None)
    shared = attrib(default=False)
    tuxbuild = attrib(default=None)

    # helper attributes
    runtime = attrib(default="podman")
    result = attrib(default="UNKNOWN")
    metadata = attrib(default={})
    output_dir = attrib(default=None)

    def __str__(self) -> str:
        tests = "[" + ", ".join(["boot"] + self.tests) + "]"
        return "{} @ {}".format(tests, self.device)

    def get_cmd(self, build_dir=None):
        cmd = (
            "python3 -m tuxrun --runtime {0} --device {1} --log-file-yaml {2}/lava-logs.yaml "
            "--log-file-html {2}/logs.html --log-file-text {2}/logs.txt --results "
            "{2}/results.json --metadata {2}/metadata.json".format(
                self.runtime, self.device, self.output_dir
            )
        ).split()

        for name in [
            "ap-romfw",
            "bios",
            "boot-args",
            "dtb",
            "fip",
            "kernel",
            "mcp-fw",
            "mcp-romfw",
            "rootfs",
            "scp-fw",
            "scp-romfw",
        ]:
            attr_name = name.replace("-", "_")
            if getattr(self, attr_name):
                cmd.extend([f"--{name}", getattr(self, attr_name)])

        if self.modules:
            cmd.extend(["--modules", self.modules])
            if self.parameters:
                modules_path = self.parameters.get("MODULES_PATH", None)
                if modules_path:
                    cmd.extend([modules_path])

        if self.parameters:
            for k, v in self.parameters.items():
                cmd.extend(["--parameters", f"{k}={v}"])

        if self.qemu_image:
            cmd.extend(["--qemu-image", self.qemu_image])

        if self.tuxbuild:
            cmd.extend(["--tuxbuild", self.tuxbuild])

        if self.tests:
            for t in self.tests:
                cmd.extend(["--tests", t])

        if self.timeouts:
            cmd.extend(["--timeouts"])
            for k, v in self.timeouts.items():
                cmd.extend([f"{k}={v}"])

        if self.overlay:
            for item in self.overlay:
                if isinstance(item, list):
                    if len(item) == 1:
                        ovl, ovl_path = item[0], "/"
                    elif len(item) == 2:
                        ovl, ovl_path = item[0], item[1]
                    else:
                        raise Exception(
                            f"overlay can't have more than 2 parameters: {item}"
                        )
                    cmd.extend(["--overlay", ovl, ovl_path])
                else:
                    cmd.extend(["--overlay", item])

        if build_dir:
            cmd.extend(["--tuxmake", build_dir])

        if self.commands:
            cmd.extend(["--", *[cmd for cmd in self.commands]])

        return cmd

    @check_container
    def submit(self, build_dir=None):
        print(f"🚀 Testing: {self}\n")
        cmd = self.get_cmd(build_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        subprocess.call(cmd)
        results_json = f"{self.output_dir}/results.json"
        if os.path.exists(results_json):
            with open(results_json, "r") as r_f:
                results = json.load(r_f)
                self.metadata = results
        self.result = (
            self.metadata.get("lava", {}).get("job", {}).get("result", "UNKNOWN")
        ).upper()
        self.format_result()

    def format_result(self):
        icon, code = "🧐", 91
        if self.result == "PASS":
            icon, code = "🎉", 92
        elif self.result == "FAIL":
            icon, code = "👹", 91
        print(f"{icon} {colorize(self.result, code)}: {self}\n")

    def summary(self, level=0):
        indentation = "    " * level
        icon, code = "🧐", 91
        if self.result == "PASS":
            icon, code = "✔", 92
        elif self.result == "FAIL":
            icon, code = "✘", 91
        color = colorize(f"{icon} {self.result}", code)
        print(f"{indentation}└── Test: {self.tests} @ {self.device}: {color}\033[0m")
