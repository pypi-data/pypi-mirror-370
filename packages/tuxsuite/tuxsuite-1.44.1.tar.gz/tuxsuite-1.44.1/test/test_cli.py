# -*- coding: utf-8 -*-

import os
import json
import pytest
import sys
import yaml
import tuxsuite.cli
import tuxsuite.build

from unittest.mock import MagicMock


from requests import HTTPError


sample_token = "Q9qMlmkjkIuIGmEAw-Mf53i_qoJ8Z2eGYCmrNx16ZLLQGrXAHRiN2ce5DGlAebOmnJFp9Ggcq9l6quZdDTtrkw"
sample_url = "https://foo.bar.tuxbuild.com/v1"


@pytest.fixture
def tuxsuite_config(tmp_path, monkeypatch, tuxauth):
    c = tmp_path / "config.ini"
    with c.open("w") as f:
        f.write("[default]\n")
        f.write(f"token={sample_token}\n")
        f.write(f"api_url={sample_url}\n")
    monkeypatch.setenv("TUXSUITE_CONFIG", str(c))
    return c


@pytest.fixture
def sample_bitbake_template():
    return """
container: ubuntu-20.04
envsetup: poky/oe-init-build-env
distro: poky
machine: qemux86-64
target: core-image-minimal
sources:
  git_trees:
    - url: git://git.yoctoproject.org/poky
      branch: dunfell
"""


sample_plan = """
version: 1
name: Simple plan
description: A simple plan
jobs:

- name: tinyconfig
  builds:
    - {toolchain: gcc-8, target_arch: i386, kconfig: tinyconfig}
    - {toolchain: gcc-9, target_arch: i386, kconfig: tinyconfig}
  test: {device: qemu-i386, tests: [ltp-smoke]}
"""


@pytest.fixture
def plan_config(tmp_path, tuxauth):
    config = tmp_path / "plan.yaml"
    with config.open("w") as f:
        f.write(sample_plan)
    return config


@pytest.fixture
def plan_builds():
    build_attrs = {
        "group": "tuxgrp",
        "project": "tuxprj",
        "git_repo": "http://github.com/torvalds/linux",
        "git_ref": "master",
        "target_arch": "arm",
        "kconfig": "defconfig",
        "build_name": "test_build_name",
        "toolchain": "gcc-9",
        "token": "test_token",
        "kbapi_url": "http://test/foo",
        "tuxapi_url": "http://tuxapi",
        "kernel_image": "Image",
    }
    builds = [
        tuxsuite.build.Build(**build_attrs, uid="build-1"),
        tuxsuite.build.Build(**build_attrs, uid="build-2"),
        tuxsuite.build.Build(**build_attrs, uid="build-3"),
        tuxsuite.build.Build(**build_attrs, uid="build-4"),
        tuxsuite.build.Build(**build_attrs, uid="build-5"),
        tuxsuite.build.Build(**build_attrs, uid="build-6"),
        tuxsuite.build.Build(**build_attrs, uid="build-7"),
        tuxsuite.build.Build(**build_attrs, uid="build-8"),
        tuxsuite.build.Build(**build_attrs, uid="build-9"),
    ]
    return builds


@pytest.fixture
def plan_builds_status_list():
    build_attrs = {
        "group": "tuxgrp",
        "project": "tuxprj",
        "git_repo": "http://github.com/torvalds/linux",
        "git_ref": "master",
        "target_arch": "arm",
        "kconfig": "defconfig",
        "build_name": "test_build_name",
        "toolchain": "gcc-9",
        "token": "test_token",
        "kbapi_url": "http://test/foo",
        "tuxapi_url": "http://tuxapi",
        "kernel_image": "Image",
    }
    builds = [
        build_attrs,
        build_attrs,
        build_attrs,
        build_attrs,
        build_attrs,
        build_attrs,
        build_attrs,
        build_attrs,
        build_attrs,
    ]
    return builds


def state(mocker, **kwargs):
    s = mocker.MagicMock()

    # defaults
    s.state = "completed"
    s.status = "pass"
    s.icon = "✓"
    s.cli_color = "white"
    s.errors = 0
    s.warnings = 0
    s.final = True

    for k, v in kwargs.items():
        setattr(s, k, v)

    return s


@pytest.fixture
def build_state(mocker):
    return state(mocker)


class TestUsage:
    def test_usage(self, monkeypatch, tuxsuite_config, capsys):
        """Test running cli() with no arguments"""
        monkeypatch.setattr(sys, "argv", ["tuxsuite"])
        with pytest.raises(SystemExit) as exc:
            tuxsuite.cli.main()
        assert exc.value.code == 2
        assert exc.type == SystemExit
        output, error = capsys.readouterr()
        assert "usage:" in error


class TestBakeCli:
    def test_bake_no_args(self, monkeypatch, tuxsuite_config, capsys):
        """Test calling bake() with no options"""
        monkeypatch.setattr(sys, "argv", ["tuxsuite", "bake"])
        with pytest.raises(SystemExit) as exc:
            tuxsuite.cli.main()
        assert exc.value.code == 2
        assert exc.type == SystemExit
        output, error = capsys.readouterr()
        assert "usage:" in error

    def test_bake_usage(self, monkeypatch, capsys):
        """Test calling bake() with --help"""
        monkeypatch.setattr(sys, "argv", ["tuxsuite", "bake", "--help"])
        with pytest.raises(SystemExit) as exc:
            tuxsuite.cli.main()
        assert exc.value.code == 0
        assert exc.type == SystemExit
        output, error = capsys.readouterr()
        assert "usage: tuxsuite bake [-h] {get,list,submit,cancel} ..." in output

    def test_bake(
        self, mocker, monkeypatch, tuxsuite_config, tmp_path, sample_bitbake_template
    ):
        template = tmp_path / "yocto.yaml"
        template.write_text(sample_bitbake_template)
        build = mocker.patch("tuxsuite.Bitbake")
        monkeypatch.setattr(sys, "argv", ["tuxsuite", "bake", "submit", f"{template}"])
        tuxsuite.cli.main()
        build.assert_called()

    def test_bake_invalid_json(self, mocker, monkeypatch, tmp_path, tuxsuite_config):
        template = tmp_path / "yocto.json"
        template.write_text("random text")
        mocker.patch("tuxsuite.Bitbake")
        monkeypatch.setattr(sys, "argv", ["tuxsuite", "bake", "submit", f"{template}"])
        with pytest.raises(SystemExit):
            tuxsuite.cli.main()

    def test_bake_no_wait(
        self, monkeypatch, mocker, tmp_path, tuxsuite_config, sample_bitbake_template
    ):
        template = tmp_path / "yocto.json"
        template.write_text(sample_bitbake_template)
        build = mocker.patch("tuxsuite.Bitbake")
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "bake",
                "submit",
                f"{template}",
                "--no-wait",
            ],
        )
        tuxsuite.cli.main()
        build.assert_called_once()

    def test_bake_manifest_error(
        self,
        monkeypatch,
        mocker,
        tmp_path,
        tuxsuite_config,
        sample_bitbake_template,
        capsys,
    ):
        template = tmp_path / "yocto.json"
        template.write_text(sample_bitbake_template)
        local_manifest = tmp_path / "local_manifest.xml"
        pinned_manifest = tmp_path / "pinned_manifest.xml"
        local_manifest.write_text("<manifest></manifest>")
        pinned_manifest.write_text("<manifest></manifest>")
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "bake",
                "submit",
                f"{template}",
                "-l",
                f"{local_manifest}",
                "-pm",
                f"{pinned_manifest}",
            ],
        )
        with pytest.raises(SystemExit) as exc:
            tuxsuite.cli.main()
        assert exc.value.code == 1
        assert exc.type == SystemExit
        output, error = capsys.readouterr()
        assert (
            error
            == "Error: Either local manifest or pinned manifest to be provided, not both\n"
        )

    def test_bake_json_out(
        self, monkeypatch, mocker, tmp_path, tuxsuite_config, sample_bitbake_template
    ):
        template = tmp_path / "yocto.json"
        template.write_text(sample_bitbake_template)
        build = mocker.patch("tuxsuite.Bitbake")
        build.return_value.status = {"sample": "value"}
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "bake",
                "submit",
                f"{template}",
                "--json-out",
                f"{tmp_path}/bake.json",
            ],
        )
        tuxsuite.cli.main()
        build.assert_called_once()
        assert os.path.exists(f"{tmp_path}/bake.json")

    def test_bake_json_out_fail(
        self,
        monkeypatch,
        mocker,
        tmp_path,
        tuxsuite_config,
        sample_bitbake_template,
        response,
    ):
        template = tmp_path / "yocto.json"
        template.write_text(sample_bitbake_template)
        build = mocker.patch(
            "tuxsuite.Bitbake",
            side_effect=HTTPError(mocker.Mock(status=500), "Unknown Error"),
        )
        build.return_value.status = {"sample": "value"}
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "bake",
                "submit",
                f"{template}",
                "--json-out",
                f"{tmp_path}/bake.json",
            ],
        )
        with pytest.raises(HTTPError):
            tuxsuite.cli.main()
        build.assert_called_once()
        assert not os.path.exists(f"{tmp_path}/bake.json")


class TestBuildCli:
    def test_build_no_args(self, monkeypatch, tuxsuite_config, capsys):
        """Test calling build() with no options"""
        monkeypatch.setattr(sys, "argv", ["tuxsuite", "build"])
        with pytest.raises(SystemExit) as exc:
            tuxsuite.cli.main()
        assert exc.value.code == 2
        assert exc.type == SystemExit
        output, error = capsys.readouterr()
        assert "tuxsuite build: error:" in error

    def test_build_usage(self, monkeypatch, tuxsuite_config, capsys):
        """Test calling build() with --help"""
        monkeypatch.setattr(sys, "argv", ["tuxsuite", "build", "--help"])
        with pytest.raises(SystemExit) as exc:
            tuxsuite.cli.main()
        assert exc.value.code == 0
        assert exc.type == SystemExit
        output, error = capsys.readouterr()
        assert "usage:" in output
        assert "config" in output
        assert "submit" in output

    def test_build(self, mocker, monkeypatch, tuxsuite_config):
        build = mocker.patch("tuxsuite.Build")
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "build",
                "--git-repo=https://git.example.com/linux.git",
                "--git-ref=master",
                "--target-arch=arm64",
                "--kconfig=defconfig",
                "--toolchain=gcc-9",
            ],
        )
        tuxsuite.cli.main()
        build.assert_called_once()

    # def test_build_quiet(self, mocker, tuxsuite_config):
    #     Build = mocker.patch("tuxsuite.Build")
    #     Build.return_value.build_data = "https://tuxsuite.example.com/abcdef0123456789/"
    #     mocker.patch("tuxsuite.cli.wait_for_object")
    #     runner = CliRunner()
    #     result = runner.invoke(
    #         tuxsuite.cli.build,
    #         [
    #             "--git-repo=https://git.example.com/linux.git",
    #             "--git-ref=master",
    #             "--target-arch=arm64",
    #             "--kconfig=defconfig",
    #             "--toolchain=gcc-9",
    #             "--quiet",
    #         ],
    #     )
    #     assert result.exit_code == 0
    #     assert "Building Linux Kernel" not in result.output
    #     assert result.output == "https://tuxsuite.example.com/abcdef0123456789/\n"

    def test_build_git_sha(self, mocker, monkeypatch, tuxsuite_config):
        build = mocker.patch("tuxsuite.Build")
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "build",
                "--git-repo=https://git.example.com/linux.git",
                "--git-sha=beefbee",
                "--target-arch=arm64",
                "--kconfig=defconfig",
                "--toolchain=gcc-9",
            ],
        )
        tuxsuite.cli.main()
        build.assert_called_once()

    def test_build_kernel_image(self, mocker, monkeypatch, tuxsuite_config):
        build = mocker.patch("tuxsuite.Build")
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "build",
                "--git-repo=https://git.example.com/linux.git",
                "--git-sha=beefbee",
                "--target-arch=arm64",
                "--kconfig=defconfig",
                "--toolchain=gcc-9",
                "--kernel-image=Image",
            ],
        )
        tuxsuite.cli.main()
        build.assert_called_once()

    def test_build_git_head(self, mocker, monkeypatch, tuxsuite_config):
        Build = mocker.patch("tuxsuite.Build")
        Build.return_value.build_data = "https://tuxsuite.example.com/abcdef0123456789/"
        get_git_head = mocker.patch("tuxsuite.gitutils.get_git_head")
        get_git_head.return_value = ("https://example.com/linux.git", "deadbeef")
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "build",
                "--git-head",
                "--target-arch=arm64",
                "--kconfig=defconfig",
                "--toolchain=gcc-9",
            ],
        )
        tuxsuite.cli.main()
        Build.assert_called_with(
            git_repo="https://example.com/linux.git",
            git_sha="deadbeef",
            git_ref=None,
            target_arch="arm64",
            kconfig=[
                "defconfig",
            ],
            toolchain="gcc-9",
            environment={},
            targets=["config", "debugkernel", "dtbs", "kernel", "modules", "xipkernel"],
            make_variables={},
            build_name=None,
            kernel_image=None,
            image_sha=None,
            no_cache=False,
            patch_series=None,
            is_public=True,
            callback=None,
            callback_headers=None,
            notify_emails=None,
        )

    def test_build_download(self, mocker, monkeypatch, tuxsuite_config):
        build = mocker.patch("tuxsuite.Build")
        download = mocker.patch("tuxsuite.download.download")
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "build",
                "--git-repo=https://git.example.com/linux.git",
                "--git-sha=beefbee",
                "--target-arch=arm64",
                "--kconfig=defconfig",
                "--toolchain=gcc-9",
                "--download",
            ],
        )
        tuxsuite.cli.main()
        build.assert_called_once()
        download.assert_called_with(mocker.ANY, ".")

    def test_build_download_output_dir(
        self, mocker, monkeypatch, tuxsuite_config, tmp_path
    ):
        mocker.patch("tuxsuite.Build")
        download = mocker.patch("tuxsuite.download.download")
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "build",
                "--git-repo=https://git.example.com/linux.git",
                "--git-ref=master",
                "--target-arch=arm64",
                "--kconfig=defconfig",
                "--toolchain=gcc-9",
                "--download",
                f"--output-dir={tmp_path}",
            ],
        )
        tuxsuite.cli.main()
        download.assert_called_with(mocker.ANY, str(tmp_path))

    def test_build_show_logs(self, mocker, monkeypatch, tuxsuite_config, capsys):
        Build = mocker.patch("tuxsuite.Build")
        build = Build.return_value
        build.status = {}
        build.status["download_url"] = "https://builds.com/21321312312/"
        mock_get = mocker.patch("tuxsuite.download.get")
        mock_response = MagicMock()
        mock_response.iter_content = MagicMock(
            return_value=[b"data_chunk1", b"data_chunk2"]
        )
        mock_get.return_value = mock_response
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "build",
                "--git-repo=https://git.example.com/linux.git",
                "--git-ref=master",
                "--target-arch=arm64",
                "--kconfig=defconfig",
                "--toolchain=gcc-9",
                "--show-logs",
            ],
        )
        tuxsuite.cli.main()
        build.build.assert_called_once()
        _, error = capsys.readouterr()
        assert "data_chunk1" in error
        assert "data_chunk2" in error

    def test_build_download_show_logs(
        self, mocker, monkeypatch, tuxsuite_config, tmp_path, capsys
    ):
        Build = mocker.patch("tuxsuite.Build")
        build = Build.return_value
        build.uid = "21321312312"
        build.build_data = "https://builds.com/21321312312/"
        (tmp_path / "21321312312").mkdir()
        (tmp_path / "21321312312" / "build.log").write_text(
            "log line 1\nlog line 2\nerror: something\n"
        )
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "build",
                "--git-repo=https://git.example.com/linux.git",
                "--git-ref=master",
                "--target-arch=arm64",
                "--kconfig=defconfig",
                "--toolchain=gcc-9",
                "--download",
                f"--output-dir={tmp_path}",
                "--show-logs",
            ],
        )
        tuxsuite.cli.main()
        build.build.assert_called_once()
        output, error = capsys.readouterr()
        assert "log line 1\nlog line 2\n" in error
        assert "error: something" in error

    def test_build_valid_environment(self, mocker, monkeypatch, tuxsuite_config):
        Build = mocker.patch("tuxsuite.Build")
        build = Build.return_value
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "build",
                "--git-repo=https://git.example.com/linux.git",
                "--git-ref=master",
                "--target-arch=arm64",
                "--kconfig=defconfig",
                "--toolchain=gcc-9",
                "-e KCONFIG_ALLCONFIG=arch/arm64/configs/defconfig",
                "-e KCONFIG_MODCONFIG=arch/arm64/configs/modconfig",
            ],
        )
        tuxsuite.cli.main()
        build.build.assert_called_once()

    def test_invalid_environment_key_value(
        self, mocker, monkeypatch, tuxsuite_config, capsys
    ):
        Build = mocker.patch("tuxsuite.Build")
        build = Build.return_value
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "build",
                "--git-repo=https://git.example.com/linux.git",
                "--git-ref=master",
                "--target-arch=arm64",
                "--kconfig=defconfig",
                "--toolchain=gcc-9",
                "-e INVALID",
            ],
        )
        with pytest.raises(SystemExit) as exc:
            tuxsuite.cli.main()
        assert exc.value.code == 1
        assert exc.type == SystemExit
        assert build.call_count == 0
        output, error = capsys.readouterr()
        assert "Key Value pair not valid:  INVALID" in error

    def test_build_valid_make_targets(self, mocker, monkeypatch, tuxsuite_config):
        Build = mocker.patch("tuxsuite.Build")
        Build.return_value.build_data = "https://tuxsuite.example.com/abcdef0123456789/"
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "build",
                "--git-repo=https://git.example.com/linux.git",
                "--git-ref=master",
                "--target-arch=arm64",
                "--kconfig=defconfig",
                "--toolchain=gcc-9",
                "dtbs",
                "config",
            ],
        )
        tuxsuite.cli.main()
        Build.assert_called_with(
            git_repo="https://git.example.com/linux.git",
            git_sha=None,
            git_ref="master",
            target_arch="arm64",
            kconfig=[
                "defconfig",
            ],
            toolchain="gcc-9",
            environment={},
            targets=["dtbs", "config"],
            make_variables={},
            build_name=None,
            kernel_image=None,
            image_sha=None,
            no_cache=False,
            patch_series=None,
            is_public=True,
            callback=None,
            callback_headers=None,
            notify_emails=None,
        )

    def test_build_no_make_targets(self, mocker, monkeypatch, tuxsuite_config):
        Build = mocker.patch("tuxsuite.Build")
        Build.return_value.build_data = "https://tuxsuite.example.com/abcdef0123456789/"
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "build",
                "--git-repo=https://git.example.com/linux.git",
                "--git-ref=master",
                "--target-arch=arm64",
                "--kconfig=defconfig",
                "--toolchain=gcc-9",
            ],
        )
        tuxsuite.cli.main()
        Build.assert_called_with(
            git_repo="https://git.example.com/linux.git",
            git_sha=None,
            git_ref="master",
            target_arch="arm64",
            kconfig=[
                "defconfig",
            ],
            toolchain="gcc-9",
            environment={},
            targets=["config", "debugkernel", "dtbs", "kernel", "modules", "xipkernel"],
            make_variables={},
            build_name=None,
            kernel_image=None,
            image_sha=None,
            no_cache=False,
            patch_series=None,
            is_public=True,
            callback=None,
            callback_headers=None,
            notify_emails=None,
        )

    def test_build_valid_make_vars(self, mocker, monkeypatch, tuxsuite_config):
        Build = mocker.patch("tuxsuite.Build")
        build = Build.return_value
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "build",
                "--git-repo=https://git.example.com/linux.git",
                "--git-ref=master",
                "--target-arch=arm64",
                "--kconfig=defconfig",
                "--toolchain=gcc-9",
                "LLVM=1",
            ],
        )
        tuxsuite.cli.main()
        build.build.assert_called_once()

    def test_build_invalid_make_vars(self, mocker, monkeypatch, tuxsuite_config):
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "build",
                "--git-repo=https://git.example.com/linux.git",
                "--git-ref=master",
                "--target-arch=arm64",
                "--kconfig=defconfig",
                "--toolchain=gcc-9",
                "LLVM=1=1",
            ],
        )
        with pytest.raises(SystemExit):
            tuxsuite.cli.main()

    def test_build_multiple_kconfig(self, mocker, monkeypatch, tuxsuite_config):
        Build = mocker.patch("tuxsuite.Build")
        Build.return_value.build_data = "https://tuxsuite.example.com/abcdef0123456789/"
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "build",
                "--git-repo=https://git.example.com/linux.git",
                "--git-ref=master",
                "--target-arch=arm64",
                "--kconfig=defconfig",
                "--kconfig=modconfig",
                "--toolchain=gcc-9",
            ],
        )
        tuxsuite.cli.main()
        Build.assert_called_with(
            git_repo="https://git.example.com/linux.git",
            git_sha=None,
            git_ref="master",
            target_arch="arm64",
            kconfig=[
                "defconfig",
                "modconfig",
            ],
            toolchain="gcc-9",
            environment={},
            targets=["config", "debugkernel", "dtbs", "kernel", "modules", "xipkernel"],
            make_variables={},
            build_name=None,
            kernel_image=None,
            image_sha=None,
            no_cache=False,
            patch_series=None,
            is_public=True,
            callback=None,
            callback_headers=None,
            notify_emails=None,
        )

    def test_build_no_wait(self, mocker, monkeypatch, tuxsuite_config, tmp_path):
        build = mocker.patch("tuxsuite.Build")
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "build",
                "--git-repo=https://git.example.com/linux.git",
                "--git-ref=master",
                "--target-arch=arm64",
                "--kconfig=defconfig",
                "--toolchain=gcc-9",
                "--no-wait",
            ],
        )
        tuxsuite.cli.main()
        build.assert_called_once()

    def test_build_json_out(self, mocker, monkeypatch, tuxsuite_config, tmp_path):
        build = mocker.patch("tuxsuite.Build")
        build.return_value.status = sample_build_result
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "build",
                "--git-repo=https://git.example.com/linux.git",
                "--git-sha=beefbee",
                "--target-arch=arm64",
                "--kconfig=defconfig",
                "--toolchain=gcc-9",
                "--json-out",
                f"{tmp_path}/build.json",
            ],
        )
        tuxsuite.cli.main()
        build.assert_called_once()
        assert os.path.exists(f"{tmp_path}/build.json")

    def test_build_json_out_fail(
        self, mocker, monkeypatch, tuxsuite_config, tmp_path, response
    ):
        build = mocker.patch(
            "tuxsuite.Build",
            side_effect=HTTPError(mocker.Mock(status=500), "Unknown Error"),
        )
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "build",
                "--git-repo=https://git.example.com/linux.git",
                "--git-sha=beefbee",
                "--target-arch=arm64",
                "--kconfig=defconfig",
                "--toolchain=gcc-9",
                "--json-out",
                f"{tmp_path}/build.json",
            ],
        )
        with pytest.raises(Exception):
            tuxsuite.cli.main()
        build.assert_called_once()
        assert not os.path.exists(f"{tmp_path}/build.json")


class TestWaitForObject:
    def test_wait_for_object_pass(self, mocker, build_state):
        build = mocker.MagicMock()
        build.watch.return_value = [build_state]
        assert tuxsuite.cli.utils.wait_for_object(build)

    def test_wait_for_object_pass_with_warnings(self, mocker, build_state):
        build = mocker.MagicMock()
        build_state.warnings = 1
        build.watch.return_value = [build_state]
        assert tuxsuite.cli.utils.wait_for_object(build)

    def test_wait_for_object_fail(self, mocker, build_state):
        build = mocker.MagicMock()
        build_state.status = "fail"
        build_state.errors = 1
        build.watch.return_value = [build_state]
        assert not tuxsuite.cli.utils.wait_for_object(build)

    def test_wait_for_object_infra_failure(self, mocker, build_state):
        build = mocker.MagicMock()
        build_state.state = "error"
        build.final = True
        build.watch.return_value = [build_state]
        assert not tuxsuite.cli.utils.wait_for_object(build)

    def test_wait_for_object_infra_failure_retried(self, mocker):
        error = state(mocker, state="error", final=False)
        retry_pass = state(mocker)
        build = mocker.MagicMock()
        build.watch.return_value = [error, retry_pass]
        assert tuxsuite.cli.utils.wait_for_object(build)


class TestPlanCli:
    def test_plan_no_args(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["tuxsuite", "plan"])
        with pytest.raises(SystemExit) as exc:
            tuxsuite.cli.main()
        assert exc.value.code == 2
        assert exc.type == SystemExit
        output, error = capsys.readouterr()
        assert "usage: tuxsuite plan" in error

    def test_plan_usage(self, monkeypatch, tuxsuite_config, capsys):
        """Test calling plan with --help"""
        monkeypatch.setattr(sys, "argv", ["tuxsuite", "plan", "--help"])
        with pytest.raises(SystemExit) as exc:
            tuxsuite.cli.main()
        assert exc.value.code == 0
        assert exc.type == SystemExit
        output, error = capsys.readouterr()
        assert "usage:" in output
        assert "submit" in output

    def test_plan_cli(self, mocker, monkeypatch, plan_config, tuxsuite_config):
        plan = mocker.patch("tuxsuite.Plan")
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "plan",
                "--git-repo=https://git.example.com/linux.git",
                "--git-ref=master",
                str(plan_config),
            ],
        )
        tuxsuite.cli.main()
        plan.assert_called_once()

    def test_plan_cli_options(
        self,
        mocker,
        monkeypatch,
        sample_patch_tgz,
        plan_config,
        tuxsuite_config,
        capsys,
    ):
        plan = mocker.patch("tuxsuite.Plan")
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "plan",
                "--git-repo=https://git.example.com/linux.git",
                "--git-ref=master",
                "--download",
                "--show-logs",
                str(plan_config),
                f"--patch-series={sample_patch_tgz}",
            ],
        )
        tuxsuite.cli.main()
        plan.assert_called_with(
            mocker.ANY,
            git_repo="https://git.example.com/linux.git",
            git_ref="master",
            git_sha=None,
            patch_series=sample_patch_tgz,
            no_cache=False,
            parameters=[],
            manifest_file=None,
            pinned_manifest=None,
            kas_override=None,
            is_public=True,
            lab="https://lkft.validation.linaro.org",
            lava_test_plans_project=None,
            callback=None,
            callback_headers=None,
            plan_callback=None,
            plan_callback_headers=None,
            notify_emails=None,
        )
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "plan",
                "--git-repo=https://git.example.com/linux.git",
                "--git-ref=master",
                "--download",
                "--show-logs",
                str(plan_config),
                f"--patch-series={sample_patch_tgz}",
                "--parameters",
                "a=b",
                "--parameters",
                "c=d",
            ],
        )
        tuxsuite.cli.main()
        plan.assert_called_with(
            mocker.ANY,
            git_repo="https://git.example.com/linux.git",
            git_ref="master",
            git_sha=None,
            patch_series=sample_patch_tgz,
            no_cache=False,
            parameters=[("a", "b"), ("c", "d")],
            manifest_file=None,
            pinned_manifest=None,
            kas_override=None,
            is_public=True,
            lab="https://lkft.validation.linaro.org",
            lava_test_plans_project=None,
            callback=None,
            callback_headers=None,
            plan_callback=None,
            plan_callback_headers=None,
            notify_emails=None,
        )

    def test_plan_empty_config(
        self, mocker, monkeypatch, plan_config, tuxsuite_config, capsys
    ):
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "plan",
                "--git-repo=https://git.example.com/linux.git",
                "--git-ref=master",
                "--job-name=kconfig",
                str(plan_config),
            ],
        )
        with pytest.raises(SystemExit):
            tuxsuite.cli.main()
        output, error = capsys.readouterr()
        assert "Empty plan, skipping" in error

    def test_plan_cli_no_wait(self, mocker, monkeypatch, tuxsuite_config, plan_config):
        plan = mocker.patch("tuxsuite.Plan")
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "plan",
                "--git-repo=https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
                "--git-ref=https://example.com/vmlinux",
                f"{plan_config}",
                "--no-wait",
            ],
        )
        tuxsuite.cli.main()
        plan.assert_called_once()

    def test_plan_cli_json_out(
        self, mocker, monkeypatch, tuxsuite_config, plan_config, tmp_path
    ):
        plan = mocker.patch("tuxsuite.Plan")
        plan.return_value.status = sample_plan_status
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "plan",
                "--git-repo=https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
                "--git-ref=https://example.com/vmlinux",
                f"{plan_config}",
                "--json-out",
                f"{tmp_path}/plan.json",
            ],
        )
        tuxsuite.cli.main()
        plan.assert_called_once()
        assert os.path.exists(f"{tmp_path}/plan.json")

    def test_plan_cli_json_out_fail(
        self, mocker, monkeypatch, tuxsuite_config, plan_config, tmp_path, response
    ):
        plan = mocker.patch(
            "tuxsuite.Plan",
            side_effect=HTTPError(mocker.Mock(status=500), "Unknown Error"),
        )
        plan.return_value.status = sample_plan_status
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "plan",
                "--git-repo=https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
                "--git-ref=https://example.com/vmlinux",
                f"{plan_config}",
                "--json-out",
                f"{tmp_path}/plan.json",
            ],
        )
        with pytest.raises(Exception):
            tuxsuite.cli.main()
        plan.assert_called_once()
        assert not os.path.exists(f"{tmp_path}/plan.json")

    def test_bake_plan_cli(
        self, mocker, monkeypatch, bake_plan_extended_config, tuxsuite_config, capsys
    ):
        plan = mocker.patch("tuxsuite.Plan")
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "plan",
                str(bake_plan_extended_config),
            ],
        )

        tuxsuite.cli.main()
        plan.assert_called_once()

    def test_plan_callback_options(
        self,
        mocker,
        monkeypatch,
        plan_config,
        tuxsuite_config,
        capsys,
    ):
        # Error when plan callback header is provided without a plan callback
        plan = mocker.patch("tuxsuite.Plan")
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "plan",
                "submit",
                "--git-repo=https://git.example.com/linux.git",
                "--git-ref=master",
                str(plan_config),
                "--plan-callback-header",
                "X-H-a: h1",
            ],
        )
        with pytest.raises(SystemExit) as exc:
            tuxsuite.cli.main()
        assert exc.value.code == 1
        assert exc.type == SystemExit
        output, error = capsys.readouterr()
        assert "Error: --plan-callback-header given without a --plan-callback" in error

        # happy flow
        plan = mocker.patch("tuxsuite.Plan")
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "plan",
                "submit",
                "--git-repo=https://git.example.com/linux.git",
                "--git-ref=master",
                str(plan_config),
                "--plan-callback-header",
                "X-H-a: h1",
                "--plan-callback-header",
                "X-H-b: h2",
                "--plan-callback=https://www.example.com/plan_callback",
            ],
        )
        tuxsuite.cli.main()
        plan.assert_called_with(
            mocker.ANY,
            git_repo="https://git.example.com/linux.git",
            git_ref="master",
            git_sha=None,
            no_cache=False,
            manifest_file=None,
            patch_series=None,
            pinned_manifest=None,
            parameters=[],
            kas_override=None,
            is_public=True,
            lab="https://lkft.validation.linaro.org",
            lava_test_plans_project=None,
            callback=None,
            callback_headers=None,
            plan_callback="https://www.example.com/plan_callback",
            plan_callback_headers={"X-H-a": "h1", "X-H-b": "h2"},
            notify_emails=None,
        )


class TestTestCli:
    def test_test_no_args(self, monkeypatch, tuxsuite_config, capsys):
        monkeypatch.setattr(sys, "argv", ["tuxsuite", "test"])
        with pytest.raises(SystemExit) as exc:
            tuxsuite.cli.main()
        assert exc.value.code == 2
        assert exc.type == SystemExit
        output, error = capsys.readouterr()
        assert "usage:" in error

    def test_test_usage(self, monkeypatch, tuxsuite_config, capsys):
        """Test calling test with --help"""
        monkeypatch.setattr(sys, "argv", ["tuxsuite", "test", "--help"])
        with pytest.raises(SystemExit) as exc:
            tuxsuite.cli.main()
        assert exc.value.code == 0
        assert exc.type == SystemExit
        output, error = capsys.readouterr()
        assert "usage:" in output
        assert "submit" in output
        assert "results" in output

    def test_test_cli(self, mocker, monkeypatch, tuxsuite_config):
        test = mocker.patch("tuxsuite.Test")
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "test",
                "--device=qemu-arm64",
                "--kernel=https://example.com/vmlinux",
                "--overlay",
                "https://example.com/overlay",
                "--overlay",
                "https://example.com/overlay",
                "/tmp",
            ],
        )
        tuxsuite.cli.main()
        test.assert_called_once()
        test.assert_called_once_with(
            device="qemu-arm64",
            kernel="https://example.com/vmlinux",
            ap_romfw=None,
            bios=None,
            dtb=None,
            mcp_fw=None,
            mcp_romfw=None,
            modules=None,
            rootfs=None,
            scp_fw=None,
            scp_romfw=None,
            fip=None,
            job_definition=None,
            parameters={},
            tests=[],
            overlays=[
                ["https://example.com/overlay", "/"],
                ["https://example.com/overlay", "/tmp"],
            ],
            timeouts={},
            boot_args=None,
            wait_for=None,
            callback=None,
            callback_headers=None,
            commands=[],
            qemu_image=None,
            tuxbuild=None,
            lab="https://lkft.validation.linaro.org",
            lava_test_plans_project=None,
            shared=False,
            host="x86_64",
            is_public=True,
            test_name=None,
            notify_emails=None,
        )

        mocker.resetall()
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "test",
                "--device=qemu-arm64",
                "--kernel=https://example.com/vmlinux",
                "--modules=https://example.com/modules.tar.xz",
                "--tests=ltp-smoke",
            ],
        )
        tuxsuite.cli.main()
        test.assert_called_once()
        test.assert_called_once_with(
            device="qemu-arm64",
            kernel="https://example.com/vmlinux",
            ap_romfw=None,
            bios=None,
            dtb=None,
            mcp_fw=None,
            mcp_romfw=None,
            modules="https://example.com/modules.tar.xz",
            rootfs=None,
            scp_fw=None,
            scp_romfw=None,
            fip=None,
            job_definition=None,
            parameters={},
            tests=["ltp-smoke"],
            overlays=[],
            timeouts={},
            boot_args=None,
            wait_for=None,
            callback=None,
            callback_headers=None,
            commands=[],
            qemu_image=None,
            tuxbuild=None,
            lab="https://lkft.validation.linaro.org",
            lava_test_plans_project=None,
            shared=False,
            host="x86_64",
            is_public=True,
            test_name=None,
            notify_emails=None,
        )

        mocker.resetall()
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "test",
                "--device=qemu-arm64",
                "--tests=ltp-smoke",
                "--wait-for=mybuilduid",
            ],
        )
        tuxsuite.cli.main()
        test.assert_called_once()
        test.assert_called_once_with(
            device="qemu-arm64",
            kernel=None,
            ap_romfw=None,
            bios=None,
            dtb=None,
            mcp_fw=None,
            mcp_romfw=None,
            modules=None,
            rootfs=None,
            scp_fw=None,
            scp_romfw=None,
            fip=None,
            job_definition=None,
            parameters={},
            tests=["ltp-smoke"],
            overlays=[],
            timeouts={},
            boot_args=None,
            wait_for="mybuilduid",
            callback=None,
            callback_headers=None,
            commands=[],
            qemu_image=None,
            tuxbuild=None,
            lab="https://lkft.validation.linaro.org",
            lava_test_plans_project=None,
            shared=False,
            host="x86_64",
            is_public=True,
            test_name=None,
            notify_emails=None,
        )

        mocker.resetall()
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "test",
                "--device=qemu-arm64",
                "--timeouts=deploy=1",
                "--timeouts=boot=2",
            ],
        )
        tuxsuite.cli.main()
        test.assert_called_once()
        test.assert_called_once_with(
            device="qemu-arm64",
            kernel=None,
            ap_romfw=None,
            bios=None,
            dtb=None,
            mcp_fw=None,
            mcp_romfw=None,
            modules=None,
            rootfs=None,
            scp_fw=None,
            scp_romfw=None,
            fip=None,
            job_definition=None,
            parameters={},
            tests=[],
            overlays=[],
            timeouts={"deploy": 1, "boot": 2},
            boot_args=None,
            wait_for=None,
            callback=None,
            callback_headers=None,
            commands=[],
            qemu_image=None,
            tuxbuild=None,
            lab="https://lkft.validation.linaro.org",
            lava_test_plans_project=None,
            shared=False,
            host="x86_64",
            is_public=True,
            test_name=None,
            notify_emails=None,
        )

        mocker.resetall()
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "test",
                "--device=fvp-morello-android",
                "--ap-romfw=tf_bl1.bin",
                "--mcp-fw=mcp_fw.bin",
                "--mcp-romfw=mcp_romfw.bin",
                "--rootfs=rootfs.ext4",
                "--scp-fw=scp_fw.bin",
                "--scp-romfw=scp_romfw.bin",
                "--fip=fip.bin",
                "--parameters=USERDATA=userdata.tar.xz",
                "--parameters=TC_URL=toolchain.tar.xz",
                "--tests=lldb",
            ],
        )
        tuxsuite.cli.main()
        test.assert_called_once()
        test.assert_called_once_with(
            device="fvp-morello-android",
            kernel=None,
            ap_romfw="tf_bl1.bin",
            bios=None,
            dtb=None,
            mcp_fw="mcp_fw.bin",
            mcp_romfw="mcp_romfw.bin",
            modules=None,
            rootfs="rootfs.ext4",
            scp_fw="scp_fw.bin",
            scp_romfw="scp_romfw.bin",
            fip="fip.bin",
            job_definition=None,
            parameters={"USERDATA": "userdata.tar.xz", "TC_URL": "toolchain.tar.xz"},
            tests=["lldb"],
            overlays=[],
            timeouts={},
            boot_args=None,
            wait_for=None,
            callback=None,
            callback_headers=None,
            commands=[],
            qemu_image=None,
            tuxbuild=None,
            lab="https://lkft.validation.linaro.org",
            lava_test_plans_project=None,
            shared=False,
            host="x86_64",
            is_public=True,
            test_name=None,
            notify_emails=None,
        )

    def test_test_cli_errors(self, mocker, monkeypatch):
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "test",
                "--device=qemu-arm64",
                "--kernel=https://example.com/vmlinux",
                "--wait-for=mybuilduid",
            ],
        )
        with pytest.raises(SystemExit):
            tuxsuite.cli.main()

    def test_test_cli_no_wait(self, mocker, monkeypatch, tuxsuite_config):
        test = mocker.patch("tuxsuite.Test")
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "test",
                "--device=qemu-arm64",
                "--kernel=https://example.com/vmlinux",
                "--no-wait",
            ],
        )
        tuxsuite.cli.main()
        test.assert_called_once()

    def test_test_cli_json_out(self, mocker, monkeypatch, tuxsuite_config, tmp_path):
        test = mocker.patch("tuxsuite.Test")
        test.return_value.status = sample_test_result
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "test",
                "--device=qemu-arm64",
                "--kernel=https://example.com/vmlinux",
                "--json-out",
                f"{tmp_path}/test.json",
            ],
        )
        tuxsuite.cli.main()
        test.assert_called_once()
        assert os.path.exists(f"{tmp_path}/test.json")

    def test_test_cli_json_out_fail(
        self, mocker, monkeypatch, tuxsuite_config, tmp_path, response
    ):
        test = mocker.patch(
            "tuxsuite.Test",
            side_effect=HTTPError(mocker.Mock(status=500), "Unknown Error"),
        )
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "test",
                "--device=qemu-arm64",
                "--kernel=https://example.com/vmlinux",
                "--no-wait",
            ],
        )
        with pytest.raises(Exception):
            tuxsuite.cli.main()
        test.assert_called_once()
        assert not os.path.exists(f"{tmp_path}/test.json")


sample_build_result = {
    "project": "ci",
    "git_repo": "https://example.com/linux.git",
    "git_ref": "master",
    "git_sha": "deadbeef",
    "build_name": "",
    "download_url": "https://builds.dev.tuxbuild.com/1sMUTVjE25tQvDmjJ8SjWblpOJr/",
    "errors_count": 0,
    "kconfig": ["tinyconfig"],
    "plan": "null",
    "result": "pass",
    "state": "finished",
    "status_message": "build completed",
    "target_arch": "arm",
    "toolchain": "gcc-9",
    "uid": "1sMUTVjE25tQvDmjJ8SjWblpOJr",
    "warnings_count": 0,
}

sample_oebuild_result = {
    "artifacts": [],
    "bblayers_conf": [],
    "container": "ubuntu-20.04",
    "distro": "rpb",
    "download_url": "https://oebuilds.tuxbuild.com/29EbSycpmLu8Nut5SoZFCwJaRER/",
    "duration": 7021,
    "environment": {},
    "envsetup": "setup-environment",
    "errors_count": 0,
    "finished_time": "2022-05-16T08:06:04.740891",
    "local_conf": [],
    "machine": "dragonboard-845c",
    "manifest_file": None,
    "name": None,
    "plan": "29EbSmPfjpbYQj8ZuaBpsiA8CbW",
    "project": "tuxsuite/alok",
    "provisioning_time": "2022-05-16T06:06:35.312683",
    "result": "pass",
    "running_time": "2022-05-16T06:09:04.709211",
    "sources": {
        "repo": {
            "branch": "qcom/dunfell",
            "manifest": "default.xml",
            "url": "https://github.com/96boards/oe-rpb-manifest.git",
        }
    },
    "state": "finished",
    "status_message": "",
    "target": "rpb-console-image rpb-console-image-test rpb-desktop-image rpb-desktop-image-test",
    "targets": [
        "rpb-console-image rpb-console-image-test rpb-desktop-image rpb-desktop-image-test"
    ],
    "uid": "1sMUTVjE25tQvDmjJ8SjWblpOJr",
    "user": "alok.ranjan@linaro.org",
    "user_agent": "tuxsuite/0.43.10",
    "waited_by": [],
    "warnings_count": 0,
}


sample_test_result = {
    "project": "ci",
    "device": "qemu-i386",
    "plan": "1sMNB0p8a3OrpUmEBgYah0Ycer9",
    "result": "fail",
    "results": {"boot": "fail"},
    "state": "finished",
    "tests": ["boot"],
    "uid": "1sMNBWLFrsOahyXQCNeiT4bgysP",
    "waiting_for": None,
}


sample_all_result = {
    "builds": {
        "count": 3,
        "next": "null",
        "results": [
            sample_build_result,
            {**sample_build_result, **dict({"warnings_count": 1})},
            {**sample_build_result, **dict({"warnings_count": 3})},
            {**sample_build_result, **dict({"result": "fail", "errors_count": 1})},
        ],
    },
    "plans": {
        "count": 1,
        "next": "null",
        "results": [
            {
                "description": "A simple plan",
                "name": "Simple plan",
                "project": "tuxsuite/senthil",
                "uid": "1sMNB0p8a3OrpUmEBgYah0Ycer9",
            }
        ],
    },
    "tests": {
        "count": 1,
        "next": "null",
        "results": [
            sample_test_result,
        ],
    },
}


sample_plan_result = {
    "builds": {
        "1": sample_build_result,
        "2": {**sample_build_result, **dict({"warnings_count": 1})},
        "3": {**sample_build_result, **dict({"warnings_count": 3})},
        "4": {**sample_build_result, **dict({"result": "fail", "errors_count": 1})},
    },
    "tests": {"1": sample_test_result},
}

sample_oe_plan_result = {
    "builds": {
        "1": sample_oebuild_result,
        "2": {**sample_oebuild_result, **dict({"warnings_count": 1})},
        "3": {**sample_oebuild_result, **dict({"warnings_count": 3})},
        "4": {**sample_oebuild_result, **dict({"result": "fail", "errors_count": 1})},
    },
    "tests": {},
}

sample_plan_status = {
    "builds": {
        "1sewrBhxNVbsURAKBjeXX8pyjwY": sample_build_result,
    },
    "tests": {
        "1sewrJ4GHQygVKvTjUxuYRK1hOh": sample_test_result,
    },
}

# sample data in list format to be consumed by from json for result status

sample_list_data = [sample_build_result, sample_oebuild_result]


@pytest.fixture
def build_result(tmp_path):
    build_json = tmp_path / "build_result.json"
    with build_json.open("w") as f:
        f.write(json.dumps(sample_build_result))
    return build_json


@pytest.fixture
def oebuild_result(tmp_path):
    build_json = tmp_path / "oebuild_result.json"
    with build_json.open("w") as f:
        f.write(json.dumps(sample_oebuild_result))
    return build_json


@pytest.fixture
def test_result(tmp_path):
    test_json = tmp_path / "test_result.json"
    with test_json.open("w") as f:
        f.write(json.dumps(sample_test_result))
    return test_json


@pytest.fixture
def plan_result(tmp_path):
    plan_json = tmp_path / "plan_result.json"
    with plan_json.open("w") as f:
        f.write(json.dumps(sample_plan_status))
    return plan_json


@pytest.fixture
def from_json_list(tmp_path):
    # this fixture return path to a file containing oebuilds/test/builds data in list format,
    # to be processed by result cli and return their status
    list_data_path = tmp_path / "from_json_list.json"
    with list_data_path.open("w") as f:
        f.write(json.dumps(sample_list_data))
    return list_data_path


class TestResultsCli:
    def test_results_cli(
        self,
        mocker,
        monkeypatch,
        tmp_path,
        tuxsuite_config,
        build_result,
        test_result,
        plan_result,
        oebuild_result,
        from_json_list,
    ):
        results = mocker.patch(
            "tuxsuite.Results.get_all", return_value=(sample_all_result, "http://api")
        )
        monkeypatch.setattr(sys, "argv", ["tuxsuite", "results", "fetch"])
        tuxsuite.cli.main()
        results.assert_called_once()

        mocker.resetall()
        results = mocker.patch(
            "tuxsuite.Results.get_build",
            return_value=(sample_build_result, "http://api"),
        )
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "results",
                "--build=1sMUTVjE25tQvDmjJ8SjWblpOJr",
                f"--json-out={tmp_path}/build_result.json",
            ],
        )
        tuxsuite.cli.main()
        results.assert_called_once()

        mocker.resetall()
        results = mocker.patch(
            "tuxsuite.Results.get_test", return_value=(sample_test_result, "http://api")
        )
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "results",
                "--test=1sMNBWLFrsOahyXQCNeiT4bgysP",
            ],
        )
        tuxsuite.cli.main()
        results.assert_called_once()

        mocker.resetall()
        results = mocker.patch(
            "tuxsuite.Results.get_plan",
            return_value=(sample_plan_result, "http://api"),
        )
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "results",
                "--plan=1sMNB0p8a3OrpUmEBgYah0Ycer9",
            ],
        )
        tuxsuite.cli.main()
        results.assert_called_once()

        mocker.resetall()
        results = mocker.patch(
            "tuxsuite.Results.get_plan",
            return_value=(sample_oe_plan_result, "http://api"),
        )
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "results",
                "--plan=29EbSmPfjpbYQj8ZuaBpsiA8CbW",
            ],
        )
        tuxsuite.cli.main()
        results.assert_called_once()

        mocker.resetall()
        results = mocker.patch(
            "tuxsuite.Results.get_oebuild",
            return_value=(sample_oebuild_result, "http://api"),
        )
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "results",
                "--oebuild=1sMUTVjE25tQvDmjJ8SjWblpOJr",
                f"--json-out={tmp_path}/oebuild_result.json",
            ],
        )
        tuxsuite.cli.main()
        results.assert_called_once()

        mocker.resetall()
        results = mocker.patch(
            "tuxsuite.Results.get_build",
            return_value=(sample_build_result, "http://api"),
        )
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "results",
                f"--from-json={build_result}",
            ],
        )
        tuxsuite.cli.main()
        results.assert_called_once()

        mocker.resetall()
        results = mocker.patch(
            "tuxsuite.Results.get_oebuild",
            return_value=(sample_oebuild_result, "http://api"),
        )
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "results",
                f"--from-json={oebuild_result}",
            ],
        )
        tuxsuite.cli.main()
        results.assert_called_once()

        mocker.resetall()
        results = mocker.patch(
            "tuxsuite.Results.get_test", return_value=(sample_test_result, "http://api")
        )
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "results",
                f"--from-json={test_result}",
            ],
        )
        tuxsuite.cli.main()
        results.assert_called_once()

        mocker.resetall()
        results = mocker.patch(
            "tuxsuite.Results.get_plan", return_value=(sample_plan_result, "http://api")
        )
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "results",
                f"--from-json={plan_result}",
            ],
        )
        tuxsuite.cli.main()
        results.assert_called_once()

        # to test --from-json of result ( data type of list )
        mocker.resetall()
        results = mocker.patch(
            "tuxsuite.Results.get_all", return_value=(sample_all_result, "http://api")
        )
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "results",
                f"--from-json={from_json_list}",
            ],
        )
        tuxsuite.cli.main()
        results.assert_called_once()

    def test_results_cli_errors(self, mocker, monkeypatch, tmp_path, tuxsuite_config):
        results = mocker.patch(
            "tuxsuite.Results.get_all",
            return_value=(sample_all_result, "http://api"),
            side_effect=tuxsuite.exceptions.URLNotFound,
        )
        monkeypatch.setattr(sys, "argv", ["tuxsuite", "results"])
        with pytest.raises(SystemExit):
            tuxsuite.cli.main()
        assert results.call_count == 0

        mocker.resetall()
        results = mocker.patch(
            "tuxsuite.Results.get_build",
            return_value=(sample_build_result, "http://api"),
            side_effect=tuxsuite.exceptions.URLNotFound,
        )
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "results",
                "--build=1sMUTVjE25tQvDmjJ8SjWblpOJr",
            ],
        )
        with pytest.raises(SystemExit):
            tuxsuite.cli.main()
        assert results.call_count == 1

        mocker.resetall()
        results = mocker.patch(
            "tuxsuite.Results.get_test",
            return_value=(sample_test_result, "http://api"),
            side_effect=tuxsuite.exceptions.URLNotFound,
        )
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "results",
                "--test=1sMNBWLFrsOahyXQCNeiT4bgysP",
            ],
        )
        with pytest.raises(SystemExit):
            tuxsuite.cli.main()
        assert results.call_count == 1

        mocker.resetall()
        results = mocker.patch(
            "tuxsuite.Results.get_plan",
            return_value=(sample_all_result, "http://api"),
            side_effect=tuxsuite.exceptions.URLNotFound,
        )
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "results",
                "--plan=1sMNB0p8a3OrpUmEBgYah0Ycer9",
            ],
        )
        with pytest.raises(SystemExit):
            tuxsuite.cli.main()
        assert results.call_count == 1

        mocker.resetall()
        results = mocker.patch(
            "tuxsuite.Results",
            side_effect=tuxsuite.exceptions.TuxSuiteError,
        )
        monkeypatch.setattr(sys, "argv", ["tuxsuite", "results"])
        with pytest.raises(SystemExit):
            tuxsuite.cli.main()
        assert results.call_count == 0


class TestBuildPatchSeries:
    def test_patch_series_error(self, mocker, monkeypatch, tuxsuite_config):
        # invalid url scheme
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "build",
                "--git-repo=https://git.example.com/linux.git",
                "--git-sha=beefbee",
                "--target-arch=arm64",
                "--kconfig=defconfig",
                "--toolchain=gcc-9",
                "--patch-series=httpsucks.patch",
            ],
        )
        with pytest.raises(Exception):
            tuxsuite.cli.main()

        mocker.resetall()
        # invalid patch file
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "build",
                "--git-repo=https://git.example.com/linux.git",
                "--git-sha=beefbee",
                "--target-arch=arm64",
                "--kconfig=defconfig",
                "--toolchain=gcc-9",
                "--patch-series=/tmp/invalidpatch",
            ],
        )
        with pytest.raises(Exception):
            tuxsuite.cli.main()

    def test_patch_series_pass(
        self, mocker, monkeypatch, sample_patch_tgz, sample_patch_mbx, tuxsuite_config
    ):
        build = mocker.patch("tuxsuite.Build")

        # valid url scheme
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "build",
                "--git-repo=https://git.example.com/linux.git",
                "--git-sha=beefbee",
                "--target-arch=arm64",
                "--kconfig=defconfig",
                "--toolchain=gcc-9",
                "--patch-series=https://www.example.com/example.tgz",
            ],
        )
        tuxsuite.cli.main()
        assert build.call_count == 1

        mocker.resetall()
        # valid patch file
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "tuxsuite",
                "build",
                "--git-repo=https://git.example.com/linux.git",
                "--git-sha=beefbee",
                "--target-arch=arm64",
                "--kconfig=defconfig",
                "--toolchain=gcc-9",
                f"--patch-series={sample_patch_tgz}",
            ],
        )
        tuxsuite.cli.main()
        assert build.call_count == 1


def test_oebuild_handle_cancel(mocker, config, response, monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "bake", "cancel", "205Yag6znViIi4oLWFVDxJC4avb"]
    )
    response.status_code = 200
    response._content = {}
    post_req = mocker.patch("requests.post", return_value=response)
    tuxsuite.cli.main()
    post_req.assert_called_with(
        "https://tuxapi.tuxsuite.com/v1/groups/tuxsuite/projects/tux/oebuilds/205Yag6znViIi4oLWFVDxJC4avb/cancel",
        headers={
            "User-Agent": "tuxsuite.cli/0.1",
            "Authorization": "Q9qMlmkjkIuIGmEAw-Mf53i_qoJ8Z2eGYCmrNx16ZLLQGrXAHRiN2ce5DGlAebOmnJFp9Ggcq9l6quZdDTtrkw",
        },
        json={},
    )
    assert post_req.call_count == 1

    # Test failure case when the response is not 200
    response.status_code = 500
    post_req = mocker.patch("requests.post", return_value=response)
    with pytest.raises(tuxsuite.exceptions.URLNotFound):
        tuxsuite.cli.main()
    assert post_req.call_count == 1


class TestRemoteVersion:
    def test_failure(self, monkeypatch, mocker, tuxsuite_config, response, capsys):
        """Test running cli() with --remote-version option failure case"""
        response.status_code = 404
        get_req = mocker.patch("requests.get", return_value=response)
        monkeypatch.setattr(sys, "argv", ["tuxsuite", "--remote-version"])
        with pytest.raises(SystemExit) as exc:
            tuxsuite.cli.main()
        assert exc.value.code == 1
        assert exc.type == SystemExit
        assert get_req.call_count == 1
        output, error = capsys.readouterr()
        assert "Error: Unable to fetch remote version" in error

    def test_happy_flow(self, mocker, monkeypatch, tuxsuite_config, response, capsys):
        """Test running cli() with --remote-version success case"""
        response.status_code = 200
        response._content = str.encode(
            json.dumps(
                {
                    "versions": {
                        "tuxbake": "0.3.1",
                        "tuxmake": "1.10.0",
                        "tuxrun": "0.36.0",
                    }
                }
            )
        )
        get_req = mocker.patch("requests.get", return_value=response)
        monkeypatch.setattr(sys, "argv", ["tuxsuite", "--remote-version"])
        with pytest.raises(SystemExit) as exc:
            tuxsuite.cli.main()
        assert exc.value.code == 0
        assert exc.type == SystemExit
        assert get_req.call_count == 1

        output, error = capsys.readouterr()
        assert "tuxbake: 0.3.1" in output
        assert "tuxmake: 1.10.0" in output
        assert "tuxrun: 0.36.0" in output


class TestKeysCli:
    def test_keys_no_args(self, monkeypatch, tuxsuite_config, capsys):
        """Test calling keys with no options"""
        monkeypatch.setattr(sys, "argv", ["tuxsuite", "keys"])
        with pytest.raises(SystemExit) as exc:
            tuxsuite.cli.main()
        assert exc.value.code == 2
        assert exc.type == SystemExit
        output, error = capsys.readouterr()
        assert "usage:" in error

    def test_keys_usage(self, monkeypatch, capsys):
        """Test calling keys with --help"""
        monkeypatch.setattr(sys, "argv", ["tuxsuite", "keys", "--help"])
        with pytest.raises(SystemExit) as exc:
            tuxsuite.cli.main()
        assert exc.value.code == 0
        assert exc.type == SystemExit
        output, error = capsys.readouterr()
        assert "usage: tuxsuite keys [-h] {add,get,delete,update}" in output
