# -*- coding: utf-8 -*-


import pytest
from unittest.mock import Mock
from tuxsuite.config import PlanConfig
from tuxsuite.exceptions import TuxSuiteError
from tuxsuite.local_plan import LocalPlan, colorize, get_new_output_dir
import json


def prepare_file(filename, data, path):
    with open(f"{path}/{filename}", "w") as f:
        json.dump(data, f, indent=4)


@pytest.fixture
def cmdargs(tmp_path):
    return Mock(tree=".", output_dir=tmp_path, runtime="docker")


@pytest.fixture(autouse=True)
def call(mocker):
    mocker.patch("subprocess.check_call")
    return mocker.patch("subprocess.call", return_value=0)


@pytest.fixture
def plan_obj(cmdargs, plan_config):
    cfg = PlanConfig("", "", plan_config)
    plan = LocalPlan(cmdargs, cfg)
    return cfg, plan


@pytest.fixture
def tuxmake_base_cmd():
    return (
        "python3 -m tuxmake --runtime {} -C {} --wrapper {} --target-arch {} "
        "--toolchain {} --output-dir {} --kconfig {}"
    )


@pytest.fixture
def tuxrun_base_cmd():
    return (
        "python3 -m tuxrun --runtime {0} --device {1} --log-file-yaml {2}/lava-logs.yaml "
        "--log-file-html {2}/logs.html --log-file-text {2}/logs.txt --results "
        "{2}/results.json --metadata {2}/metadata.json"
    )


def test_get_new_output_dir(tmp_path):
    assert str(tmp_path / "plan") in str(get_new_output_dir(tmp_path))
    assert ".cache/tuxsuite/plan/" in str(get_new_output_dir(None))


class TestLocalPlan:
    def test_check_tools(self, mocker, capsys):
        mocker.patch("subprocess.check_call", side_effect=FileNotFoundError)
        # case: 'tuxmake/tuxrun' not installed
        with pytest.raises(SystemExit):
            LocalPlan.check_tools("docker")
        _, err = capsys.readouterr()
        assert (
            "Package 'tuxmake' not installed, but can be installed with:\npip3 install tuxmake"
            in err
        )

    def test_local_plan_config(self, build_plan, test_plan, plan_config):
        # case: single build plan
        plan_cfg = PlanConfig("local plan", "local plan desc", build_plan)
        assert plan_cfg.name == "local plan"
        assert plan_cfg.description == "local plan desc"
        assert len(plan_cfg.plan) == 1
        build = plan_cfg.plan[0]
        assert build["build"] is not None
        assert build["tests"] == []

        # case: single test plan
        plan_cfg = PlanConfig("local plan", "local plan desc", test_plan)
        assert plan_cfg.name == "local plan"
        assert plan_cfg.description == "local plan desc"
        assert len(plan_cfg.plan) == 1
        test = plan_cfg.plan[0]
        assert test["build"] is None
        assert test["tests"] is not None

        # case: with job-name
        plan_cfg = PlanConfig(
            "local plan", "local plan desc", plan_config, ["simple-gcc"]
        )
        assert plan_cfg.name == "local plan"
        assert plan_cfg.description == "local plan desc"
        assert len(plan_cfg.plan) == 1

    def test_submit(self, plan_obj, call):
        plan_cfg, plan = plan_obj
        assert len(plan.builds) == 11
        assert len(plan.tests) == 6

        # builds and tests
        for b, d in zip(plan.builds, plan_cfg.plan):
            assert b.target_arch == d["build"]["target_arch"]
            assert b.kconfig == d["build"]["kconfig"]
            assert b.toolchain == d["build"]["toolchain"]
            assert len(b.dependent_tests) == len(d["tests"])
            for t1, t2 in zip(b.dependent_tests, d["tests"]):
                assert t1.device == t2.get("device")
                assert t1.kernel == t2.get("kernel")
                assert t1.tests == t2.get("tests", [])

        plan.submit()
        # Ideally total call would be 30. But as calls are mocked,
        # Dependent test would not have been called due to build
        # results being unknown.
        assert call.call_count == 17

    def test_summary(self, cmdargs, build_plan, capsys):
        plan_cfg = PlanConfig("local plan", "local plan desc", build_plan)
        plan = LocalPlan(cmdargs, plan_cfg)
        plan.summary()
        out, err = capsys.readouterr()
        assert err == ""
        assert "Build: clang-nightly @ i386" in out

    def test_ret_code(self, plan_obj, tmp_path):
        _, plan = plan_obj

        def reset_ret_code(plan):
            plan.__ret_code__ = None

        # case: Initially all results are "UNKNOWN"
        assert plan.ret_code == 1

        # case: "PASS" all builds
        reset_ret_code(plan)
        for b in plan.builds:
            b.result = "PASS"
        assert plan.ret_code == 1

        # case: "PASS" all tests
        reset_ret_code(plan)
        for t in plan.tests:
            t.result = "PASS"
        assert plan.ret_code == 1

        # case: "PASS" all build dependent tests
        reset_ret_code(plan)
        for b in plan.builds:
            for t in b.dependent_tests:
                t.result = "PASS"

        assert plan.ret_code == 0

        # case: mix of "PASS" and "FAIL"
        # All build dependent test "PASS"
        reset_ret_code(plan)
        b_len, _ = len(plan.builds), len(plan.tests)
        for b in plan.builds[b_len // 2 :]:
            b.result = "FAIL"
        assert all([b.result == "PASS"] for b in plan.builds[: b_len // 2])
        assert all([b.result == "FAIL"] for b in plan.builds[b_len // 2 :])
        assert plan.ret_code == 1
        reset_ret_code(plan)
        for t in plan.tests:
            t.result = "FAIL"
        assert plan.ret_code == 1


class TestLocalBuild:
    def test_get_cmd(self, plan_obj, tuxmake_base_cmd):
        _, plan = plan_obj
        build = plan.builds[0]
        cmd = tuxmake_base_cmd.format(
            build.runtime,
            build.tree,
            build.wrapper,
            build.target_arch,
            build.toolchain,
            build.output_dir,
            build.kconfig,
        ).split()
        assert build.get_cmd() == cmd

        # case: add kconfig list
        build.kconfig = ["defconfig", "https://kconfig/url", "CONFIG_EXT4_F=y"]
        cmd.pop()
        cmd += "defconfig --kconfig-add https://kconfig/url --kconfig-add CONFIG_EXT4_F=y".split()
        assert build.get_cmd() == cmd

        # case: add environment
        build.environment = {"A": "B", "C": "D"}
        cmd += "-e A=B -e C=D".split()
        assert build.get_cmd() == cmd

        # cae: add make variable
        build.make_variables = {"ARCH": "A", "SUBARCH": "B"}
        cmd += "ARCH=A SUBARCH=B".split()
        assert build.get_cmd() == cmd

        # case: add kernel image
        kernel_image = "test_kernel_image"
        build.kernel_image = kernel_image
        cmd += f"--kernel-image {kernel_image}".split()
        assert build.get_cmd() == cmd

        # case: add targets
        targets = ["config", "modules"]
        build.targets = targets
        cmd += targets
        assert build.get_cmd() == cmd

        # case: with patch series
        with pytest.raises(TuxSuiteError):
            build.patch_series = "https://patch-series.mbox"
            build.get_cmd()

    def test_submit(self, plan_obj, call, tmp_path):
        _, plan = plan_obj
        build = plan.builds[0]
        build.output_dir = tmp_path

        # case: successful submit
        prepare_file("metadata.json", {"results": {"status": "PASS"}}, tmp_path)
        build.submit()
        assert build.result == "PASS"
        assert call.call_count == 1
        args = call.call_args[0][0]
        cmd = build.get_cmd()
        assert args == cmd

        # case: successful submit with tuxmake build dir
        prepare_file("metadata.json", {"results": {"status": "FAIL"}}, tmp_path)
        build.submit()
        assert build.result == "FAIL"
        assert call.call_count == 2
        args = call.call_args[0][0]
        cmd = build.get_cmd()
        assert args == cmd

        # case: unsuccessful submit
        call.reset_mock()
        call.return_value = 1
        with pytest.raises(SystemExit):
            build.submit()
        call.call_count == 1

    def test_submit_tests(self, plan_obj, call, capsys):
        _, plan = plan_obj
        build = plan.builds[0]
        build.result = "PASS"

        # case: successful submit
        build.submit_tests()
        assert call.call_count == 1
        args = call.call_args[0][0]
        assert "tuxrun" in args

        # case: unsuccessful submit
        build.result = "FAIL"
        build.submit_tests()
        args = call.call_args[0][0]
        out, _ = capsys.readouterr()
        assert "Build failed, skipping tests" in out

    @pytest.mark.parametrize(
        "items", [("🎉", 92, "PASS"), ("👹", 91, "FAIL"), ("🧐", 91, "UNKNOWN")]
    )
    def test_format_result(self, capsys, plan_obj, items):
        _, plan = plan_obj
        build = plan.builds[0]

        icon, code, result = items
        build.result = result
        build.format_result()
        out, _ = capsys.readouterr()
        assert (
            out == f"{icon} {colorize(result, code)}: i386 with tinyconfig @ gcc-8\n\n"
        )

    @pytest.mark.parametrize(
        "items", [("✔", 92, "PASS"), ("✘", 91, "FAIL"), ("🧐", 91, "UNKNOWN")]
    )
    def test_summary(self, plan_obj, items, capsys):
        _, plan = plan_obj
        build = plan.builds[0]

        icon, code, result = items
        build.result = result
        build.summary()
        out, _ = capsys.readouterr()
        assert (
            f"Build: {build.toolchain} @ {build.target_arch}: {colorize(f'{icon} {result}', code)}"
            in out
        )


class TestLocalTest:
    def test_get_cmd(self, plan_obj, tuxrun_base_cmd):
        _, plan = plan_obj
        test = plan.tests[0]
        test.tests = []
        test.kernel = None
        cmd = tuxrun_base_cmd.format(
            test.runtime,
            test.device,
            test.output_dir,
        ).split()
        assert test.get_cmd() == cmd

        # case: add kernel
        kernel = "https://storage.tuxboot.com/arm64/Image"
        test.kernel = kernel
        cmd += ["--kernel", kernel]
        test.get_cmd() == cmd

        # case: add modules
        modules = "https://example.com/modules.tar.xz"
        test.modules = modules
        cmd += ["--modules", modules]
        assert test.get_cmd() == cmd

        # case: add modules with MODULES_PATH in parameters
        parameters = {"MODULES_PATH": "/usr/"}
        test.parameters = parameters
        cmd += ["/usr/", "--parameters", "MODULES_PATH=/usr/"]
        assert test.get_cmd() == cmd

        # case: add parameters
        parameters.update(
            {
                "USERDATA": "https://storage.tuxboot.com/fvp-morello-android/userdata.tar.xz"
            }
        )
        test.parameters = parameters
        cmd += [
            "--parameters",
            "USERDATA=https://storage.tuxboot.com/fvp-morello-android/userdata.tar.xz",
        ]
        assert test.get_cmd() == cmd

        # case: add qemu image
        qemu_image = "docker.io/qemu/qemu:latest"
        test.qemu_image = qemu_image
        cmd += ["--qemu-image", qemu_image]
        assert test.get_cmd() == cmd

        # case: add tuxbuild
        tuxbuild = "https://builds.tuxbuild.com/<ksuid>/"
        test.tuxbuild = tuxbuild
        cmd += ["--tuxbuild", tuxbuild]
        assert test.get_cmd() == cmd

        # case: add tests
        tests = ["boot", "ltp-smoke"]
        test.tests = tests
        cmd += ["--tests", "boot", "--tests", "ltp-smoke"]

        # case: add timeouts
        timeouts = {"deploy": 10, "boot": 12, "ltp-smoke": 32}
        test.timeouts = timeouts
        cmd += ["--timeouts", "deploy=10", "boot=12", "ltp-smoke=32"]
        assert test.get_cmd() == cmd

        # case: add overlay
        overlay = [
            ["https://example.com/script.sh", "/"],
            ["single_overlay"],
            "str_overlay",
        ]
        test.overlay = overlay
        cmd += [
            "--overlay",
            "https://example.com/script.sh",
            "/",
            "--overlay",
            "single_overlay",
            "/",
            "--overlay",
            "str_overlay",
        ]
        assert test.get_cmd() == cmd

        # case: overlay exception
        with pytest.raises(Exception):
            test.overlay = [["a", "b", "c"]]
            test.get_cmd()
        test.overlay = overlay

        # case: add commands
        commands = ["ls", "pwd", "cd ltp && ./ltp"]
        test.commands = commands
        cmd += ["--", *commands]
        assert test.get_cmd() == cmd

        assert cmd == [
            "python3",
            "-m",
            "tuxrun",
            "--runtime",
            "docker",
            "--device",
            "qemu-arm64",
            "--log-file-yaml",
            f"{test.output_dir}/lava-logs.yaml",
            "--log-file-html",
            f"{test.output_dir}/logs.html",
            "--log-file-text",
            f"{test.output_dir}/logs.txt",
            "--results",
            f"{test.output_dir}/results.json",
            "--metadata",
            f"{test.output_dir}/metadata.json",
            "--kernel",
            "https://storage.tuxboot.com/arm64/Image",
            "--modules",
            "https://example.com/modules.tar.xz",
            "/usr/",
            "--parameters",
            "MODULES_PATH=/usr/",
            "--parameters",
            "USERDATA=https://storage.tuxboot.com/fvp-morello-android/userdata.tar.xz",
            "--qemu-image",
            "docker.io/qemu/qemu:latest",
            "--tuxbuild",
            "https://builds.tuxbuild.com/<ksuid>/",
            "--tests",
            "boot",
            "--tests",
            "ltp-smoke",
            "--timeouts",
            "deploy=10",
            "boot=12",
            "ltp-smoke=32",
            "--overlay",
            "https://example.com/script.sh",
            "/",
            "--overlay",
            "single_overlay",
            "/",
            "--overlay",
            "str_overlay",
            "--",
            "ls",
            "pwd",
            "cd ltp && ./ltp",
        ]

    def test_submit(self, call, plan_obj, tmp_path):
        _, plan = plan_obj
        test = plan.tests[0]
        test.output_dir = tmp_path

        # case: successful submit
        prepare_file("results.json", {"lava": {"job": {"result": "pass"}}}, tmp_path)
        test.submit()
        assert test.result == "PASS"
        assert call.call_count == 1
        args = call.call_args[0][0]
        cmd = test.get_cmd()
        assert args == cmd

        # case: successful submit with tuxmake build dir
        prepare_file("results.json", {"lava": {"job": {"result": "fail"}}}, tmp_path)
        test.submit(build_dir="/tmp/tuxmake/")
        assert test.result == "FAIL"
        assert call.call_count == 2
        args = call.call_args[0][0]
        cmd = test.get_cmd()
        assert args == cmd + ["--tuxmake", "/tmp/tuxmake/"]

        # case: unsuccessful submit
        call.reset_mock()
        call.return_value = 1
        test.submit()
        call.call_count == 1
        assert test.result == "FAIL"

    @pytest.mark.parametrize(
        "items", [("🎉", 92, "PASS"), ("👹", 91, "FAIL"), ("🧐", 91, "UNKNOWN")]
    )
    def test_format_result(self, capsys, plan_obj, items):
        _, plan = plan_obj
        test = plan.tests[0]

        icon, code, result = items
        test.result = result
        test.format_result()
        out, _ = capsys.readouterr()
        assert (
            out
            == f"{icon} {colorize(result, code)}: [boot, ltp-smoke] @ qemu-arm64\n\n"
        )

    @pytest.mark.parametrize(
        "items", [("✔", 92, "PASS"), ("✘", 91, "FAIL"), ("🧐", 91, "UNKNOWN")]
    )
    def test_summary(self, plan_obj, items, capsys):
        _, plan = plan_obj
        test = plan.tests[0]

        icon, code, result = items
        test.result = result
        test.summary()
        out, _ = capsys.readouterr()
        assert (
            f"Test: {test.tests} @ {test.device}: {colorize(f'{icon} {result}', code)}"
            in out
        )
