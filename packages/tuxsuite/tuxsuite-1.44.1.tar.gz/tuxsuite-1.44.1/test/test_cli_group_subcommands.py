# -*- coding: utf-8 -*-

import json
import sys

import pytest

import tuxsuite.cli


@pytest.fixture
def group_json():
    group = {
        "name": "tuxsuite",
        "builds": {"daily": 325, "monthly": 1727, "overall": 84429},
        "oebuilds": {"daily": 0, "monthly": 13, "overall": 835},
        "plans": {"daily": 49, "monthly": 176, "overall": 7211},
        "tests": {"daily": 33, "monthly": 299, "overall": 241718},
        "duration": {"builds": 242477, "oebuilds": 13114, "tests": 37127},
        "limits": {"builds": 100000, "oebuilds": 400, "tests": 5000},
        "lava_devices": [],
    }
    return json.dumps(group).encode("utf-8")


@pytest.fixture
def group_list_json():
    group_list = {"count": 2, "results": ["tuxsuite", "linaro"], "next": None}
    return json.dumps(group_list).encode("utf-8")


@pytest.fixture
def group_bills_json():
    group_bills = {
        "count": 2,
        "results": [
            {
                "group": "tuxsuite",
                "date": "2021-03-01",
                "count": {"builds": 8282, "oebuilds": 0, "plans": 55, "tests": 102464},
                "duration": {"builds": 83761, "oebuilds": 0, "tests": 477168},
            },
            {
                "group": "tuxsuite",
                "date": "2021-04-01",
                "count": {"builds": 3688, "oebuilds": 0, "plans": 109, "tests": 2339},
                "duration": {"builds": 424014, "oebuilds": 0, "tests": 19937200},
            },
        ],
        "next": None,
    }
    return json.dumps(group_bills).encode("utf-8")


def test_group_handle_bills(
    mocker, group_bills_json, config, response, monkeypatch, tmp_path
):
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "group", "bills", "tuxsuite"])
    response.status_code = 200
    response._content = group_bills_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1

    # Test csv out
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "group", "bills", "tuxsuite", "--csv"]
    )
    response.status_code = 200
    response._content = group_bills_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1

    # Test --json
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "group", "bills", "tuxsuite", "--json"]
    )
    response.status_code = 200
    response._content = group_bills_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1

    # Test --json-out
    json_path = f"{tmp_path}/group.json"
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "group", "bills", "tuxsuite", "--json-out", json_path]
    )
    response.status_code = 200
    response._content = group_bills_json
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


def test_group_handle_get(mocker, group_json, config, response, monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "group", "get", "tuxsuite"])
    response.status_code = 200
    response._content = group_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1

    # Test --json
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "group", "get", "tuxsuite", "--json"])
    response.status_code = 200
    response._content = group_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1

    # Test --json-out
    json_path = f"{tmp_path}/group.json"
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "group", "get", "tuxsuite", "--json-out", json_path]
    )
    response.status_code = 200
    response._content = group_json
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


def test_group_handle_list(
    mocker, group_list_json, config, response, monkeypatch, tmp_path
):
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "group", "list"])
    response.status_code = 200
    response._content = group_list_json
    list_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert list_req.call_count == 1

    # Test --json
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "group", "list", "--json"])
    response.status_code = 200
    response._content = group_list_json
    list_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert list_req.call_count == 1

    # Test --json-out
    json_path = f"{tmp_path}/group.json"
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "group", "list", "--json-out", json_path]
    )
    response.status_code = 200
    response._content = group_list_json
    list_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert list_req.call_count == 1
    assert len(json.load(open(json_path, "r"))) > 0

    # Test failure case when the response is not 200
    response.status_code = 500
    list_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(NotImplementedError):
        tuxsuite.cli.main()
    assert list_req.call_count == 1
