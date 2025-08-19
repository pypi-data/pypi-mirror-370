# -*- coding: utf-8 -*-

import sys
import json
import pytest
import tuxsuite


@pytest.fixture
def oebuild_json():
    oebuild = {
        "project": "tuxsuite/alok",
        "uid": "2WZzJFyuUkHHqKbRtIrqDDXV0GY",
        "plan": "None",
        "distro": "oniro-linux",
        "machine": "qemux86-64",
        "container": "ubuntu-20.04",
        "environment": {"TEMPLATECONF": "../oniro/flavours/linux"},
        "local_conf": [],
        "bblayers_conf": [],
        "artifacts": [],
        "targets": ["intltool-native"],
        "name": "",
        "envsetup": "oe-core/oe-init-build-env",
        "user": "alok.ranjan@linaro.org",
        "token_name": "test",
        "user_agent": "tuxsuite/1.26.0",
        "download_url": (
            "https://alok.dev.storage.tuxsuite.com/public/tuxsuite/alok/oebuilds/2WZzJFyuUkHHqKbRtIrqDDXV0GY/"
        ),
        "sources": {
            "repo": {
                "branch": "kirkstone",
                "manifest": "default.xml",
                "url": "https://gitlab.eclipse.org/eclipse/oniro-core/oniro",
            }
        },
        "state": "finished",
        "result": "pass",
        "waited_by": [],
        "errors_count": 0,
        "warnings_count": 0,
        "running_time": "2023-10-10T16:24:00.593896",
        "finished_time": "2023-10-10T16:25:28.997015",
        "manifest_file": "None",
        "pinned_manifest": "None",
        "kas_override": "None",
        "no_cache": False,
        "is_public": True,
        "callback": "https://webhook.site/a014cd4b-9243-478f-8b0e-a87cd03f405c",
        "extraconfigs": [],
        "is_canceling": False,
        "provisioning_time": "2023-10-10T16:20:16.667581",
        "duration": 93,
        "setup_duration": 150,
        "status_message": "",
    }
    return json.dumps(oebuild).encode("utf-8")


@pytest.fixture
def oebuild_json_cancel():
    oebuild = {
        "project": "tuxsuite/alok",
        "uid": "2UgtHiSOEXW276PoljEV6tXp92K",
        "plan": "2UgtHeXipCJFMNJ1raYwjq3KLRB",
        "distro": "rpb",
        "machine": "dragonboard-845c",
        "container": "ubuntu-20.04",
        "environment": {},
        "local_conf": [],
        "bblayers_conf": [],
        "artifacts": [],
        "targets": [
            "rpb-console-image rpb-console-image-test rpb-desktop-image rpb-desktop-image-test"
        ],
        "name": "",
        "envsetup": "setup-environment",
        "user": "alok.ranjan@linaro.org",
        "token_name": "test",
        "user_agent": "tuxsuite/1.25.1",
        "download_url": (
            "https://alok.dev.storage.tuxsuite.com/public/tuxsuite/alok/oebuilds/2UgtHiSOEXW276PoljEV6tXp92K/"
        ),
        "sources": {
            "repo": {
                "branch": "qcom/dunfell",
                "manifest": "default.xml",
                "url": "https://github.com/96boards/oe-rpb-manifest.git",
            }
        },
        "state": "finished",
        "result": "canceled",
        "waited_by": ["TEST#2UgtHwjoGs9CinugZDJt1jKaQ6h"],
        "errors_count": 0,
        "warnings_count": 0,
        "running_time": "2023-08-30T05:25:43.477681",
        "finished_time": "2023-08-30T05:42:50.641441",
        "manifest_file": "None",
        "pinned_manifest": "None",
        "kas_override": "None",
        "no_cache": False,
        "is_public": True,
        "callback": "None",
        "extraconfigs": [],
        "is_canceling": True,
        "provisioning_time": "2023-08-30T05:22:45.623496",
        "duration": 1029,
        "setup_duration": 136,
        "status_message": "Build canceled on request",
    }
    return json.dumps(oebuild).encode("utf-8")


@pytest.fixture
def bake_list_json():
    oebuild_list = {
        "count": 2,
        "results": [
            {
                "project": "tuxsuite/alok",
                "uid": "2da81Bp5e03RuOmhIWVQJhtv7UJ",
                "plan": None,
                "distro": "poky-tiny",
                "machine": "qemux86",
                "container": "ubuntu-20.04",
                "environment": {},
                "local_conf": [
                    "INHERIT += 'buildstats buildstats-summary'",
                    "TCLIBC := 'musl'",
                ],
                "bblayers_conf": [],
                "envsetup": "poky/oe-init-build-env",
                "download_url": (
                    "https://alok.dev.storage.tuxsuite.com/public/tuxsuite/alok/oebuilds/2da81Bp5e03RuOmhIWVQJhtv7UJ/"
                ),
                "user": "alok.ranjan@linaro.org",
                "state": "finished",
                "result": "pass",
                "waited_by": [],
                "errors_count": 0,
                "warnings_count": 0,
                "provisioning_time": "2024-03-12T09:10:10.257468",
                "running_time": "2024-03-12T09:12:33.187068",
                "finished_time": "2024-03-12T09:14:34.264444",
                "targets": ["core-image-base core-image-minimal"],
                "target": None,
                "duration": 126,
                "status_message": "",
                "manifest_file": None,
            },
            {
                "project": "tuxsuite/alok",
                "uid": "2dZv9mXVABiAmkBh7oeeoDrRMZS",
                "plan": None,
                "distro": "poky-tiny",
                "machine": "qemux86",
                "container": "ubuntu-20.04",
                "environment": {},
                "local_conf": [
                    "INHERIT += 'buildstats buildstats-summary'",
                    "TCLIBC := 'musl'",
                ],
                "bblayers_conf": [],
                "envsetup": "poky/oe-init-build-env",
                "download_url": (
                    "https://alok.dev.storage.tuxsuite.com/public/tuxsuite/alok/oebuilds/2dZv9mXVABiAmkBh7oeeoDrRMZS/"
                ),
                "user": "alok.ranjan@linaro.org",
                "state": "finished",
                "result": "pass",
                "waited_by": [],
                "errors_count": 0,
                "warnings_count": 0,
                "provisioning_time": "2024-03-12T07:24:25.325816",
                "running_time": "2024-03-12T07:27:41.358228",
                "finished_time": "2024-03-12T08:21:27.674203",
                "targets": ["core-image-base core-image-minimal"],
                "target": None,
                "duration": 3229,
                "status_message": "",
                "manifest_file": None,
            },
        ],
        "next": None,
    }
    return json.dumps(oebuild_list).encode("utf-8")


def test_bake_handle_get(mocker, oebuild_json, config, response, monkeypatch, tmp_path):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "bake", "get", "2WZzJFyuUkHHqKbRtIrqDDXV0GY"]
    )
    response.status_code = 200
    response._content = oebuild_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1

    # Test --json
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "bake", "get", "2WZzJFyuUkHHqKbRtIrqDDXV0GY", "--json"],
    )
    response.status_code = 200
    response._content = oebuild_json
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
    json_path = f"{tmp_path}/oebuild.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "bake",
            "get",
            "2WZzJFyuUkHHqKbRtIrqDDXV0GY",
            "--json-out",
            json_path,
        ],
    )
    response.status_code = 200
    response._content = oebuild_json
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
            "bake",
            "get",
            "2WZzJFyuUkHHqKbRtIrqDDXV0GY",
            "--list-artifacts",
        ],
    )
    response.status_code = 200
    response._content = oebuild_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 2
    assert "storage.tuxsuite.com" in get_req.call_args[0][0]

    # case: --list-artifacts with path
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "bake",
            "get",
            "2WZzJFyuUkHHqKbRtIrqDDXV0GY",
            "--list-artifacts",
            "dir_A",
        ],
    )
    response.status_code = 200
    response._content = oebuild_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 2
    assert "storage.tuxsuite.com" in get_req.call_args[0][0]
    assert "/dir_A/" in get_req.call_args[0][0]

    # case: --list-artifacts with download option
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "bake",
            "get",
            "2WZzJFyuUkHHqKbRtIrqDDXV0GY",
            "--list-artifacts",
            "-d",
            str(tmp_path),
        ],
    )
    response.status_code = 200
    response._content = oebuild_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 2
    assert "storage.tuxsuite.com" in get_req.call_args[0][0]

    # case: --list-artifacts with path and download option
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "bake",
            "get",
            "2WZzJFyuUkHHqKbRtIrqDDXV0GY",
            "--list-artifacts",
            "dir_A",
            "-d",
            str(tmp_path),
        ],
    )
    response.status_code = 200
    response._content = oebuild_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 2
    assert "storage.tuxsuite.com" in get_req.call_args[0][0]
    assert "/dir_A/" in get_req.call_args[0][0]

    # case: --download-artifacts with path
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "bake",
            "get",
            "2WZzJFyuUkHHqKbRtIrqDDXV0GY",
            "--download-artifacts",
            str(tmp_path),
        ],
    )
    response.status_code = 200
    response._content = oebuild_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 2
    assert "storage.tuxsuite.com" in get_req.call_args[0][0]


def test_bake_handle_list(
    mocker, bake_list_json, config, response, monkeypatch, tmp_path
):
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "bake", "list", "--limit", "1"])
    monkeypatch.setattr("sys.stdout.isatty", lambda: True)
    mocker.patch("builtins.input", side_effect=KeyboardInterrupt)
    response.status_code = 200
    response._content = bake_list_json
    list_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(SystemExit) as exit:
        tuxsuite.cli.main()
    assert exit.value.code == 0
    assert list_req.call_count == 1

    # case: --json
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "bake", "list", "--json"])
    response.status_code = 200
    response._content = bake_list_json
    list_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert exit.value.code == 0
    assert list_req.call_count == 1

    # case: --json-out
    json_path = f"{tmp_path}/test.json"
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "bake", "list", "--json-out", json_path]
    )
    response.status_code = 200
    response._content = bake_list_json
    list_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert exit.value.code == 0
    assert list_req.call_count == 1
    assert len(json.load(open(json_path, "r"))) == 2

    # case: --json-out with --limit
    json_path = f"{tmp_path}/test.json"
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "bake", "list", "--json-out", json_path, "--limit", "1"],
    )
    response.status_code = 200
    response._content = bake_list_json
    list_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert exit.value.code == 0
    assert list_req.call_count == 1
    assert len(json.load(open(json_path, "r"))) == 1

    # Test failure case when the response is not 200
    response.status_code = 500
    list_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(NotImplementedError):
        tuxsuite.cli.main()
    assert list_req.call_count == 1


def test_bake_handle_cancel_get(
    mocker, oebuild_json_cancel, config, response, monkeypatch
):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "bake", "get", "2UgtHiSOEXW276PoljEV6tXp92K"]
    )
    response.status_code = 200
    response._content = oebuild_json_cancel
    get_req_cancel = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req_cancel.call_count == 1
