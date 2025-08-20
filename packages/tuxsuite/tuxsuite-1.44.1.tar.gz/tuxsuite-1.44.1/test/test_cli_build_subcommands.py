# -*- coding: utf-8 -*-

import sys
import json
import pytest
import tuxsuite


@pytest.fixture
def build_json():
    build = {
        "project": "tuxsuite/senthil",
        "uid": "205Yag6znViIi4oLWFVDxJC4avb",
        "plan": None,
        "kconfig": ["tinyconfig"],
        "target_arch": "i386",
        "toolchain": "gcc-9",
        "build_name": "",
        "client_token": "7c76a710-57e4-4f67-84e2-bc592b3f18d9",
        "environment": {},
        "make_variables": {},
        "targets": [],
        "git_repo": "https://github.com/Linaro/linux-canaries.git",
        "git_ref": "v5.9",
        "git_sha": "bbf5c979011a099af5dc76498918ed7df445635b",
        "download_url": "https://builds.stylesen.dev.tuxbuild.com/205Yag6znViIi4oLWFVDxJC4avb/",
        "kernel_image": "",
        "user": "senthil.kumaran@linaro.org",
        "state": "finished",
        "result": "pass",
        "waited_by": [],
        "errors_count": 0,
        "warnings_count": 2,
        "provisioning_time": "2021-10-27T11:59:40.574911",
        "running_time": "2021-10-27T12:01:10.929870",
        "finished_time": "2021-10-27T12:03:22.168886",
        "duration": 131,
        "kernel_version": "5.9.0",
        "kernel_image_name": "bzImage",
        "status_message": "build completed",
        "git_describe": "v5.9",
    }
    return json.dumps(build).encode("utf-8")


@pytest.fixture
def build_json_cancel():
    build = {
        "project": "tuxsuite/senthil",
        "uid": "205Yag6znViIi4oLWFVDxJC4avc",
        "plan": None,
        "kconfig": ["tinyconfig"],
        "target_arch": "i386",
        "toolchain": "gcc-9",
        "build_name": "",
        "client_token": "7c76a710-57e4-4f67-84e2-bc592b3f18d9",
        "environment": {},
        "make_variables": {},
        "targets": [],
        "git_repo": "https://github.com/Linaro/linux-canaries.git",
        "git_ref": "v5.9",
        "git_sha": "bbf5c979011a099af5dc76498918ed7df445635b",
        "download_url": "https://builds.stylesen.dev.tuxbuild.com/205Yag6znViIi4oLWFVDxJC4avc/",
        "kernel_image": "",
        "user": "senthil.kumaran@linaro.org",
        "state": "finished",
        "result": "canceled",
        "waited_by": [],
        "errors_count": 0,
        "warnings_count": 2,
        "provisioning_time": "2021-10-27T11:59:40.574911",
        "running_time": "2021-10-27T12:01:10.929870",
        "finished_time": "2021-10-27T12:03:22.168886",
        "duration": 131,
        "kernel_version": "5.9.0",
        "kernel_image_name": "bzImage",
        "status_message": "build canceled",
        "git_describe": "v5.9",
    }
    return json.dumps(build).encode("utf-8")


@pytest.fixture
def build_json_error():
    build = {
        "project": "tuxsuite/senthil",
        "uid": "205Yag6znViIi4oLWFVDxJC4avz",
        "plan": None,
        "kconfig": ["tinyconfig"],
        "target_arch": "i386",
        "toolchain": "gcc-9",
        "build_name": "",
        "client_token": "7c76a710-57e4-4f67-84e2-bc592b3f18d9",
        "environment": {},
        "make_variables": {},
        "targets": [],
        "git_repo": "https://github.com/Linaro/linux-canaries.git",
        "git_ref": "v5.9",
        "git_sha": "bbf5c979011a099af5dc76498918ed7df445635b",
        "download_url": "https://builds.stylesen.dev.tuxbuild.com/205Yag6znViIi4oLWFVDxJC4avz/",
        "kernel_image": "",
        "user": "senthil.kumaran@linaro.org",
        "state": "finished",
        "result": "error",
        "waited_by": [],
        "errors_count": 1,
        "warnings_count": 2,
        "provisioning_time": "2021-10-27T11:59:40.574911",
        "running_time": "2021-10-27T12:01:10.929870",
        "finished_time": "2021-10-27T12:03:22.168886",
        "duration": 131,
        "kernel_version": "5.9.0",
        "kernel_image_name": "bzImage",
        "status_message": "build error",
        "git_describe": "v5.9",
    }
    return json.dumps(build).encode("utf-8")


@pytest.fixture
def build_json_unknown():
    build = {
        "project": "tuxsuite/senthil",
        "uid": "205Yag6znViIi4oLWFVDxJC4avz",
        "plan": None,
        "kconfig": ["tinyconfig"],
        "target_arch": "i386",
        "toolchain": "gcc-9",
        "build_name": "",
        "client_token": "7c76a710-57e4-4f67-84e2-bc592b3f18d9",
        "environment": {},
        "make_variables": {},
        "targets": [],
        "git_repo": "https://github.com/Linaro/linux-canaries.git",
        "git_ref": "v5.9",
        "git_sha": "bbf5c979011a099af5dc76498918ed7df445635b",
        "download_url": "https://builds.stylesen.dev.tuxbuild.com/205Yag6znViIi4oLWFVDxJC4avz/",
        "kernel_image": "",
        "user": "senthil.kumaran@linaro.org",
        "state": "finished",
        "result": "unknown",
        "waited_by": [],
        "errors_count": 0,
        "warnings_count": 2,
        "provisioning_time": "2021-10-27T11:59:40.574911",
        "running_time": "2021-10-27T12:01:10.929870",
        "finished_time": "2021-10-27T12:03:22.168886",
        "duration": 131,
        "kernel_version": "5.9.0",
        "kernel_image_name": "bzImage",
        "status_message": "build running",
        "git_describe": "v5.9",
    }
    return json.dumps(build).encode("utf-8")


@pytest.fixture
def build_list_json():
    build_list = {
        "count": 1,
        "results": [
            {
                "project": "tuxsuite/senthil",
                "uid": "207i1AaccpFZvAMsGFfjas952dX",
                "plan": None,
                "kconfig": ["tinyconfig"],
                "target_arch": "arm64",
                "toolchain": "gcc-10",
                "build_name": "",
                "client_token": "4f30586f-1ca9-4242-bb41-7fe9e2be8a78",
                "environment": {},
                "make_variables": {},
                "targets": [],
                "git_repo": "https://github.com/torvalds/linux.git",
                "git_ref": "master",
                "git_sha": "1fc596a56b334f4d593a2b49e5ff55af6aaa0816",
                "download_url": "https://builds.stylesen.dev.tuxbuild.com/207i1AaccpFZvAMsGFfjas952dX/",
                "kernel_image": "",
                "user": "senthil.kumaran@linaro.org",
                "state": "finished",
                "result": "pass",
                "waited_by": [],
                "errors_count": 0,
                "warnings_count": 0,
                "provisioning_time": "2021-10-28T06:16:48.279774",
                "running_time": "2021-10-28T06:19:06.621554",
                "finished_time": "2021-10-28T06:22:58.242564",
                "duration": 233,
                "build_status": "pass",
                "kernel_version": "5.15.0-rc7",
                "kernel_image_name": "Image.gz",
                "status_message": "build completed",
                "git_describe": "v5.15-rc7-33-g1fc596a56b33",
            }
        ],
        "next": None,
    }
    return json.dumps(build_list).encode("utf-8")


def test_build_handle_config(mocker, config, response, monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "build", "config", "205Yag6znViIi4oLWFVDxJC4avb"]
    )
    response.status_code = 200
    response._content = b'{"download_url": "b"}'
    config_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert config_req.call_count == 2

    # Test failure case when the response is not 200
    response.status_code = 500
    config_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(NotImplementedError):
        tuxsuite.cli.main()
    assert config_req.call_count == 1


def test_build_handle_get(mocker, build_json, config, response, monkeypatch, tmp_path):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "build", "get", "205Yag6znViIi4oLWFVDxJC4avb"]
    )
    response.status_code = 200
    response._content = build_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1

    # Test --json
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "build", "get", "205Yag6znViIi4oLWFVDxJC4avb", "--json"],
    )
    response.status_code = 200
    response._content = build_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1

    # Test failure case when the response is not 200
    response.status_code = 500
    get_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(NotImplementedError):
        tuxsuite.cli.main()
    assert get_req.call_count == 1

    # Test --json-out
    json_path = f"{tmp_path}/build.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "build",
            "get",
            "205Yag6znViIi4oLWFVDxJC4avb",
            "--json-out",
            json_path,
        ],
    )
    response.status_code = 200
    response._content = build_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1
    assert len(json.load(open(json_path, "r"))) > 0

    # case: --list-artifacts
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "build",
            "get",
            "205Yag6znViIi4oLWFVDxJC4avb",
            "--list-artifacts",
        ],
    )
    response.status_code = 200
    response._content = build_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 2
    assert "builds.stylesen.dev.tuxbuild.com" in get_req.call_args[0][0]

    # case: --list-artifacts with path
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "build",
            "get",
            "205Yag6znViIi4oLWFVDxJC4avb",
            "--list-artifacts",
            "dir_A",
        ],
    )
    response.status_code = 200
    response._content = build_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 2
    assert "builds.stylesen.dev.tuxbuild.com" in get_req.call_args[0][0]
    assert "/dir_A" in get_req.call_args[0][0]

    # case: --list-artifacts with download option
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "build",
            "get",
            "205Yag6znViIi4oLWFVDxJC4avb",
            "--list-artifacts",
            "-d",
            str(tmp_path),
        ],
    )
    response.status_code = 200
    response._content = build_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 2
    assert "builds.stylesen.dev.tuxbuild.com" in get_req.call_args[0][0]

    # case: --list-artifacts with path and download option
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "build",
            "get",
            "205Yag6znViIi4oLWFVDxJC4avb",
            "--list-artifacts",
            "dir_A",
            "-d",
            str(tmp_path),
        ],
    )
    response.status_code = 200
    response._content = build_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 2
    assert "builds.stylesen.dev.tuxbuild.com" in get_req.call_args[0][0]
    assert "/dir_A" in get_req.call_args[0][0]

    # case: --download-artifacts with path
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "build",
            "get",
            "205Yag6znViIi4oLWFVDxJC4avb",
            "--download-artifacts",
            str(tmp_path),
        ],
    )
    response.status_code = 200
    response._content = build_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 2
    assert "builds.stylesen.dev.tuxbuild.com" in get_req.call_args[0][0]


def test_build_handle_cancel_get(
    mocker, build_json_cancel, config, response, monkeypatch
):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "build", "get", "205Yag6znViIi4oLWFVDxJC4avc"]
    )
    response.status_code = 200
    response._content = build_json_cancel
    get_req_cancel = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req_cancel.call_count == 1


def test_build_handle_unknown_get(
    mocker, build_json_unknown, config, response, monkeypatch
):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "build", "get", "205Yag6znViIi4oLWFVDxJC4avz"]
    )
    response.status_code = 200
    response._content = build_json_unknown
    get_req_unknown = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req_unknown.call_count == 1


def test_build_handle_cancel(mocker, build_json, config, response, monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "build", "cancel", "205Yag6znViIi4oLWFVDxJC4avb"]
    )
    response.status_code = 200
    response._content = build_json
    post_req = mocker.patch("requests.post", return_value=response)
    tuxsuite.cli.main()
    post_req.assert_called_with(
        "https://tuxapi.tuxsuite.com/v1/groups/tuxsuite/projects/tux/builds/205Yag6znViIi4oLWFVDxJC4avb/cancel",
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


def test_build_handle_list(
    mocker, build_list_json, config, response, monkeypatch, tmp_path
):
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "build", "list", "--limit", "1"])
    monkeypatch.setattr("sys.stdout.isatty", lambda: True)
    mocker.patch("builtins.input", side_effect=KeyboardInterrupt)
    response.status_code = 200
    response._content = build_list_json
    list_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(SystemExit) as exit:
        tuxsuite.cli.main()
    assert exit.value.code == 0
    assert list_req.call_count == 1

    # Test --json
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "build", "list", "--json"])
    response.status_code = 200
    response._content = build_list_json
    list_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert exit.value.code == 0
    assert list_req.call_count == 1

    # Test failure case when the response is not 200
    response.status_code = 500
    list_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(NotImplementedError):
        tuxsuite.cli.main()
    assert list_req.call_count == 1

    # Test --json-out
    json_path = f"{tmp_path}/build.json"
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "build", "list", "--json-out", json_path]
    )
    response.status_code = 200
    response._content = build_list_json
    list_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert exit.value.code == 0
    assert list_req.call_count == 1
    assert len(json.load(open(json_path, "r"))) > 0


def test_build_handle_logs(mocker, config, response, monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "build", "logs", "205Yag6znViIi4oLWFVDxJC4avb"]
    )
    response.status_code = 200
    response._content = b'{"download_url": "b"}'
    logs_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert logs_req.call_count == 2

    # Test failure case when the response is not 200
    response.status_code = 500
    logs_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(NotImplementedError):
        tuxsuite.cli.main()
    assert logs_req.call_count == 1

    # Test when log is unavailable - due to infra error
    response.status_code = 404
    logs_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert logs_req.call_count == 1


def test_build_handle_wait(mocker, build_json, config, response, monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "build", "wait", "205Yag6znViIi4oLWFVDxJC4avb"],
    )
    response.status_code = 200
    response._content = build_json
    wait_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert wait_req.call_count == 1

    # Test failure case when the response is not 200
    response.status_code = 500
    wait_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(NotImplementedError):
        tuxsuite.cli.main()
    assert wait_req.call_count == 1


def test_build_handle_cancel_wait_get(
    mocker, build_json_cancel, config, response, monkeypatch
):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "build", "wait", "205Yag6znViIi4oLWFVDxJC4avc"]
    )
    response.status_code = 200
    response._content = build_json_cancel
    get_req_cancel = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req_cancel.call_count == 1


def test_build_handle_unknown_wait_get(
    mocker, build_json_unknown, config, response, monkeypatch
):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "build", "wait", "205Yag6znViIi4oLWFVDxJC4avz"]
    )
    response.status_code = 200
    response._content = build_json_unknown
    get_req_unknown = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req_unknown.call_count == 1


def test_build_handle_error_wait_get(
    mocker, build_json_error, config, response, monkeypatch
):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "build", "wait", "205Yag6znViIi4oLWFVDxJC4avz"]
    )
    response.status_code = 200
    response._content = build_json_error
    get_req_unknown = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req_unknown.call_count == 1
