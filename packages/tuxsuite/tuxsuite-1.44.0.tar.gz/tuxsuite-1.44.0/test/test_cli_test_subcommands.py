# -*- coding: utf-8 -*-

import sys
import json
import pytest
import tuxsuite

from unittest import mock


@pytest.fixture
def test_json():
    test = {
        "project": "tuxsuite/senthil",
        "device": "qemu-x86_64",
        "uid": "1t2giU7PHbVdarV0ZFIohd0PvFb",
        "kernel": "https://storage.tuxboot.com/x86_64/bzImage",
        "ap_romfw": None,
        "mcp_fw": None,
        "mcp_romfw": None,
        "modules": None,
        "parameters": None,
        "rootfs": None,
        "scp_fw": None,
        "scp_romfw": None,
        "fip": None,
        "tests": ["boot", "ltp-smoke"],
        "user": None,
        "user_agent": None,
        "state": "finished",
        "result": "pass",
        "results": {"boot": "pass", "ltp-smoke": "pass"},
        "plan": "1t2ghz9i7oeLHa2pW1a8EsR1RLP",
        "download_url": "https://storage.tuxsuite.com/uid1/",
        "waiting_for": None,
        "boot_args": None,
        "provisioning_time": "2021-05-25T19:58:44.093685",
        "running_time": "2021-05-25T19:58:44.493457",
        "finished_time": "2021-05-25T19:59:45.311189",
        "duration": 61,
        "test_name": "",
    }
    return json.dumps(test).encode("utf-8")


@pytest.fixture
def test_error_json():
    test = {
        "project": "tuxsuite/senthil",
        "device": "qemu-x86_64",
        "uid": "1t2giU7PHbVdarV0ZFIohd0PvFb",
        "kernel": "https://storage.tuxboot.com/x86_64/bzImage",
        "ap_romfw": None,
        "mcp_fw": None,
        "mcp_romfw": None,
        "modules": None,
        "parameters": None,
        "rootfs": None,
        "scp_fw": None,
        "scp_romfw": None,
        "fip": None,
        "tests": ["boot", "ltp-smoke"],
        "user": None,
        "user_agent": None,
        "state": "finished",
        "result": "error",
        "results": {"boot": "pass", "ltp-smoke": "pass"},
        "plan": "1t2ghz9i7oeLHa2pW1a8EsR1RLP",
        "download_url": "https://storage.tuxsuite.com/uid1/",
        "waiting_for": None,
        "boot_args": None,
        "provisioning_time": "2021-05-25T19:58:44.093685",
        "running_time": "2021-05-25T19:58:44.493457",
        "finished_time": "2021-05-25T19:59:45.311189",
        "duration": 61,
        "test_name": "",
    }
    return json.dumps(test).encode("utf-8")


@pytest.fixture
def test_fail_json():
    test = {
        "project": "tuxsuite/senthil",
        "device": "qemu-x86_64",
        "uid": "1t2giU7PHbVdarV0ZFIohd0PvFb",
        "kernel": "https://storage.tuxboot.com/x86_64/bzImage",
        "ap_romfw": None,
        "mcp_fw": None,
        "mcp_romfw": None,
        "modules": None,
        "parameters": None,
        "rootfs": None,
        "scp_fw": None,
        "scp_romfw": None,
        "fip": None,
        "tests": ["boot", "ltp-smoke"],
        "user": None,
        "user_agent": None,
        "state": "finished",
        "result": "fail",
        "results": {"boot": "pass", "ltp-smoke": "pass"},
        "plan": "1t2ghz9i7oeLHa2pW1a8EsR1RLP",
        "download_url": "https://storage.tuxsuite.com/uid1/",
        "waiting_for": None,
        "boot_args": None,
        "provisioning_time": "2021-05-25T19:58:44.093685",
        "running_time": "2021-05-25T19:58:44.493457",
        "finished_time": "2021-05-25T19:59:45.311189",
        "duration": 61,
        "test_name": "",
    }
    return json.dumps(test).encode("utf-8")


@pytest.fixture
def test_canceled_json():
    test = {
        "project": "tuxsuite/senthil",
        "device": "qemu-x86_64",
        "uid": "1t2giU7PHbVdarV0ZFIohd0PvFa",
        "kernel": "https://storage.tuxboot.com/x86_64/bzImage",
        "ap_romfw": None,
        "mcp_fw": None,
        "mcp_romfw": None,
        "modules": None,
        "parameters": None,
        "rootfs": None,
        "scp_fw": None,
        "scp_romfw": None,
        "fip": None,
        "tests": ["boot", "ltp-smoke"],
        "user": None,
        "user_agent": None,
        "state": "finished",
        "result": "canceled",
        "results": {"boot": "canceled", "ltp-smoke": "canceled"},
        "plan": "1t2ghz9i7oeLHa2pW1a8EsR1RLP",
        "download_url": "https://storage.tuxsuite.com/uid1/",
        "waiting_for": None,
        "boot_args": None,
        "provisioning_time": "2021-05-25T19:58:44.093685",
        "running_time": "2021-05-25T19:58:44.493457",
        "finished_time": "2021-05-25T19:59:45.311189",
        "duration": 61,
        "test_name": "",
    }
    return json.dumps(test).encode("utf-8")


@pytest.fixture
def test_unknown_json():
    test = {
        "project": "tuxsuite/senthil",
        "device": "qemu-x86_64",
        "uid": "1t2giU7PHbVdarV0ZFIohd0PvFz",
        "kernel": "https://storage.tuxboot.com/x86_64/bzImage",
        "ap_romfw": None,
        "mcp_fw": None,
        "mcp_romfw": None,
        "modules": None,
        "parameters": None,
        "rootfs": None,
        "scp_fw": None,
        "scp_romfw": None,
        "fip": None,
        "tests": ["boot", "ltp-smoke"],
        "user": None,
        "user_agent": None,
        "state": "finished",
        "result": "unknown",
        "results": {"boot": "unknown", "ltp-smoke": "unknown"},
        "plan": "1t2ghz9i7oeLHa2pW1a8EsR1RLP",
        "download_url": "https://storage.tuxsuite.com/uid1/",
        "waiting_for": None,
        "boot_args": None,
        "provisioning_time": "2021-05-25T19:58:44.093685",
        "running_time": "2021-05-25T19:58:44.493457",
        "finished_time": "2021-05-25T19:59:45.311189",
        "duration": 61,
        "test_name": "",
    }
    return json.dumps(test).encode("utf-8")


@pytest.fixture
def test_list_json():
    test_list = {
        "count": 3,
        "results": [
            {
                "project": "tuxsuite/senthil",
                "device": "qemu-i386",
                "uid": "1t2gzwpOVhU7ahus1FvS7swPeG7",
                "kernel": "https://storage.tuxboot.com/i386/bzImage",
                "ap_romfw": None,
                "mcp_fw": None,
                "mcp_romfw": None,
                "modules": None,
                "parameters": None,
                "rootfs": None,
                "scp_fw": None,
                "scp_romfw": None,
                "fip": None,
                "tests": ["boot", "ltp-smoke"],
                "user": None,
                "user_agent": None,
                "state": "finished",
                "result": "pass",
                "results": {"boot": "pass", "ltp-smoke": "pass"},
                "plan": "1t2gzLqkWHi2ldxDETNMVHPYBYo",
                "download_url": "https://storage.tuxsuite.com/uid1/",
                "waiting_for": None,
                "boot_args": None,
                "provisioning_time": "2021-05-25T20:01:03.057613",
                "running_time": "2021-05-25T20:01:03.318610",
                "finished_time": "2021-05-25T20:01:54.490403",
                "duration": 51,
                "test_name": "",
            },
            {
                "project": "tuxsuite/senthil",
                "device": "qemu-i386",
                "uid": "1t2gzwpOVhU7ahus1FvS7swPeG7",
                "kernel": "https://storage.tuxboot.com/i386/bzImage",
                "ap_romfw": None,
                "mcp_fw": None,
                "mcp_romfw": None,
                "modules": None,
                "parameters": None,
                "rootfs": None,
                "scp_fw": None,
                "scp_romfw": None,
                "fip": None,
                "tests": ["boot", "ltp-smoke"],
                "user": None,
                "user_agent": None,
                "state": "finished",
                "result": "canceled",
                "results": {"boot": "canceled", "ltp-smoke": "canceled"},
                "plan": "1t2gzLqkWHi2ldxDETNMVHPYBYo",
                "download_url": "https://storage.tuxsuite.com/uid2/",
                "waiting_for": None,
                "boot_args": None,
                "provisioning_time": "2021-05-25T20:01:03.057613",
                "running_time": "2021-05-25T20:01:03.318610",
                "finished_time": "2021-05-25T20:01:54.490403",
                "duration": 51,
                "test_name": "",
            },
            {
                "project": "tuxsuite/senthil",
                "device": "qemu-i386",
                "uid": "1t2gzwpOVhU7ahus1FvS7swPeG7",
                "kernel": "https://storage.tuxboot.com/i386/bzImage",
                "ap_romfw": None,
                "mcp_fw": None,
                "mcp_romfw": None,
                "modules": None,
                "parameters": None,
                "rootfs": None,
                "scp_fw": None,
                "scp_romfw": None,
                "fip": None,
                "tests": ["boot", "ltp-smoke"],
                "user": None,
                "user_agent": None,
                "state": "finished",
                "result": "unknown",
                "results": {"boot": "unknown", "ltp-smoke": "unknown"},
                "plan": "1t2gzLqkWHi2ldxDETNMVHPYBYo",
                "download_url": "https://storage.tuxsuite.com/uid3/",
                "waiting_for": None,
                "boot_args": None,
                "provisioning_time": "2021-05-25T20:01:03.057613",
                "running_time": "2021-05-25T20:01:03.318610",
                "finished_time": "2021-05-25T20:01:54.490403",
                "duration": 51,
                "test_name": "",
            },
        ],
        "next": None,
    }
    return json.dumps(test_list).encode("utf-8")


@pytest.fixture
def result_json():
    result = {
        "lava": {
            "validate": {"result": "pass"},
            "file-download": {
                "duration": "3.78",
                "level": "1.5.1",
                "namespace": "caommon",
                "result": "pass",
            },
            "test-overlay": {
                "duration": "0.00",
                "level": "1.1.3.2",
                "namespace": "common",
                "result": "pass",
            },
            "test-1": {
                "duration": "0.00",
                "level": "1.1.3.2",
                "namespace": "common",
                "result": "fail",
            },
            "test-2": {
                "duration": "0.00",
                "level": "1.1.3.2",
                "namespace": "common",
                "result": "error",
            },
        }
    }
    return json.dumps(result).encode("utf-8")


def test_test_handle_get(mocker, test_json, config, response, monkeypatch, tmp_path):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "test", "get", "1t2giU7PHbVdarV0ZFIohd0PvFb"]
    )
    response.status_code = 200
    response._content = test_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1

    # Test --json
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "test", "get", "1t2giU7PHbVdarV0ZFIohd0PvFb", "--json"],
    )
    response.status_code = 200
    response._content = test_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1

    # Test --json-out
    json_path = f"{tmp_path}/test.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "test",
            "get",
            "1t2giU7PHbVdarV0ZFIohd0PvFb",
            "--json-out",
            json_path,
        ],
    )
    response.status_code = 200
    response._content = test_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1
    assert len(json.load(open(json_path, "r"))) > 0

    # Test failure case when the response is not 200
    response.status_code = 500
    get_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(NotImplementedError):
        tuxsuite.cli.main()
    assert get_req.call_count == 1

    # case: --list-artifacts
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "test",
            "get",
            "1t2giU7PHbVdarV0ZFIohd0PvFb",
            "--list-artifacts",
        ],
    )
    response.status_code = 200
    response._content = test_json
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
            "test",
            "get",
            "1t2giU7PHbVdarV0ZFIohd0PvFb",
            "--list-artifacts",
            "dir_A",
        ],
    )
    response.status_code = 200
    response._content = test_json
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
            "test",
            "get",
            "1t2giU7PHbVdarV0ZFIohd0PvFb",
            "--list-artifacts",
            "-d",
            str(tmp_path),
        ],
    )
    response.status_code = 200
    response._content = test_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 2
    assert "storage.tuxsuite.com" in get_req.call_args[0][0]

    # case: --list-artifacts with path and  download option
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "test",
            "get",
            "1t2giU7PHbVdarV0ZFIohd0PvFb",
            "--list-artifacts",
            "dir_A",
            "-d",
            str(tmp_path),
        ],
    )
    response.status_code = 200
    response._content = test_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 2
    assert "storage.tuxsuite.com" in get_req.call_args[0][0]
    assert "/dir_A" in get_req.call_args[0][0]

    # case: --download-artifacts with path
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "test",
            "get",
            "1t2giU7PHbVdarV0ZFIohd0PvFb",
            "--download-artifacts",
            str(tmp_path),
        ],
    )
    response.status_code = 200
    response._content = test_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 2
    assert "storage.tuxsuite.com" in get_req.call_args[0][0]


def test_test_handle_cancel(mocker, test_json, config, response, monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "test", "cancel", "21t2giU7PHbVdarV0ZFIohd0PvFb"]
    )
    response.status_code = 200
    response._content = test_json
    post_req = mocker.patch("requests.post", return_value=response)
    tuxsuite.cli.main()
    post_req.assert_called_with(
        "https://tuxapi.tuxsuite.com/v1/groups/tuxsuite/projects/tux/tests/21t2giU7PHbVdarV0ZFIohd0PvFb/cancel",
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


def test_test_handle_get_canceled(
    mocker, test_canceled_json, config, response, monkeypatch
):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "test", "get", "1t2giU7PHbVdarV0ZFIohd0PvFa"]
    )
    response.status_code = 200
    response._content = test_canceled_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1


def test_test_handle_get_unknown(
    mocker, test_unknown_json, config, response, monkeypatch
):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "test", "get", "1t2giU7PHbVdarV0ZFIohd0PvFz"]
    )
    response.status_code = 200
    response._content = test_unknown_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1


def test_test_handle_get_error(mocker, test_error_json, config, response, monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "test", "get", "1t2giU7PHbVdarV0ZFIohd0PvFb"]
    )
    response.status_code = 200
    response._content = test_error_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1


def test_test_handle_get_fail(mocker, test_fail_json, config, response, monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "test", "get", "1t2giU7PHbVdarV0ZFIohd0PvFb"]
    )
    response.status_code = 200
    response._content = test_fail_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1


def test_test_handle_list(
    mocker, test_list_json, config, response, monkeypatch, tmp_path
):
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "test", "list", "--limit", "1"])
    monkeypatch.setattr("sys.stdout.isatty", lambda: True)
    mocker.patch("builtins.input", side_effect=KeyboardInterrupt)
    response.status_code = 200
    response._content = test_list_json
    list_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(SystemExit) as exit:
        tuxsuite.cli.main()
    assert exit.value.code == 0
    assert list_req.call_count == 1

    # Test --json
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "test", "list", "--json"])
    response.status_code = 200
    response._content = test_list_json
    list_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert exit.value.code == 0
    assert list_req.call_count == 1

    # Test --json-out
    json_path = f"{tmp_path}/test.json"
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "test", "list", "--json-out", json_path]
    )
    response.status_code = 200
    response._content = test_list_json
    list_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert exit.value.code == 0
    assert list_req.call_count == 1
    assert len(json.load(open(json_path, "r"))) > 0

    # Test failure case when the response is not 200
    response.status_code = 500
    list_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(NotImplementedError):
        tuxsuite.cli.main()
    assert list_req.call_count == 1


def test_test_handle_logs(mocker, config, response, monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "test", "logs", "1yiYkYq26HbT5i304xElM5Czj2d"]
    )

    def mock_request(url, **kwargs):
        if (
            url
            == "https://tuxapi.tuxsuite.com/v1/groups/tuxsuite/projects/tux/tests/1yiYkYq26HbT5i304xElM5Czj2d"
        ):
            return mock.Mock(
                status_code=200,
                json=lambda: {
                    "download_url": (
                        "https://storage.tuxsuite.com/public/tuxsuite/tux/tests/"
                        "1yiYkYq26HbT5i304xElM5Czj2d/"
                    )
                },
            )
        elif (
            url
            == "https://storage.tuxsuite.com/public/tuxsuite/tux/tests/1yiYkYq26HbT5i304xElM5Czj2d/lava-logs.yaml"
        ):
            return mock.Mock(
                status_code=200,
                text=b"""- {"dt": "2021-09-27T09:58:08.499180", "lvl": "info", "msg": "msg-1"}
- {"dt": "2021-09-27T09:58:08.499454", "lvl": "info", "msg": "msg-2"}
- {"dt": "2021-09-27T09:58:08.500845", "lvl": "debug", "msg": "msg-3"}
""",
            )

    with mock.patch("requests.get", side_effect=mock_request) as logs_req:
        tuxsuite.cli.main()
        assert logs_req.call_count == 2

    # test raw output
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "test", "logs", "1yiYkYq26HbT5i304xElM5Czj2d", "--raw"],
    )
    with mock.patch("requests.get", side_effect=mock_request) as logs_req:
        tuxsuite.cli.main()
        assert logs_req.call_count == 2

    # Test failure case when the response is not 200
    response.status_code = 500
    logs_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(NotImplementedError):
        tuxsuite.cli.main()
    assert logs_req.call_count == 1
    assert logs_req.call_count == 1

    # Test failure case when the response is not 200
    response.status_code = 500
    logs_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(NotImplementedError):
        tuxsuite.cli.main()
    assert logs_req.call_count == 1


def test_test_handle_results(mocker, config, result_json, response, monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "test", "results", "1yiYkYq26HbT5i304xElM5Czj2d"]
    )

    def mock_request(url, **kwargs):
        if (
            url
            == "https://tuxapi.tuxsuite.com/v1/groups/tuxsuite/projects/tux/tests/1yiYkYq26HbT5i304xElM5Czj2d"
        ):
            return mock.Mock(
                status_code=200,
                json=lambda: {
                    "download_url": (
                        "https://storage.tuxsuite.com/public/tuxsuite/tux/tests/"
                        "1yiYkYq26HbT5i304xElM5Czj2d/"
                    )
                },
            )
        elif (
            url
            == "https://storage.tuxsuite.com/public/tuxsuite/tux/tests/1yiYkYq26HbT5i304xElM5Czj2d/results.json"
        ):
            return mock.Mock(status_code=200, text=result_json)

    with mock.patch("requests.get", side_effect=mock_request) as logs_req:
        tuxsuite.cli.main()
        assert logs_req.call_count == 2

    # test raw output
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "test", "results", "1yiYkYq26HbT5i304xElM5Czj2d", "--raw"],
    )
    with mock.patch("requests.get", side_effect=mock_request) as logs_req:
        tuxsuite.cli.main()
        assert logs_req.call_count == 2

    # Test failure case when the response is not 200
    response.status_code = 500
    requests_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(NotImplementedError):
        tuxsuite.cli.main()
    assert requests_req.call_count == 1


def test_test_handle_wait(mocker, test_json, config, response, monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "test", "wait", "1t2giU7PHbVdarV0ZFIohd0PvFb"]
    )
    response.status_code = 200
    response._content = test_json
    wait_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert wait_req.call_count == 1

    # Test failure case when the response is not 200
    response.status_code = 500
    wait_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(NotImplementedError):
        tuxsuite.cli.main()
    assert wait_req.call_count == 1


def test_test_handle_wait_canceled(
    mocker, test_canceled_json, config, response, monkeypatch
):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "test", "wait", "1t2giU7PHbVdarV0ZFIohd0PvFa"]
    )
    response.status_code = 200
    response._content = test_canceled_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1


def test_test_handle_wait_unknown(
    mocker, test_unknown_json, config, response, monkeypatch
):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "test", "wait", "1t2giU7PHbVdarV0ZFIohd0PvFz"]
    )
    response.status_code = 200
    response._content = test_unknown_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1


def test_test_handle_wait_error(mocker, test_error_json, config, response, monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "test", "wait", "1t2giU7PHbVdarV0ZFIohd0PvFb"]
    )
    response.status_code = 200
    response._content = test_error_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1


def test_test_handle_wait_fail(mocker, test_fail_json, config, response, monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "test", "wait", "1t2giU7PHbVdarV0ZFIohd0PvFb"]
    )
    response.status_code = 200
    response._content = test_fail_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1
