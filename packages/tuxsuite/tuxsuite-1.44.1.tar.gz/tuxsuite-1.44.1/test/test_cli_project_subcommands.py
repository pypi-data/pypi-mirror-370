# -*- coding: utf-8 -*-

import json
import sys

import pytest

import tuxsuite.cli


@pytest.fixture
def project_json():
    project = {
        "name": "tuxsuite/remi",
        "builds": {"daily": 0, "monthly": 1, "overall": 1856},
        "oebuilds": {"daily": 0, "monthly": 0, "overall": 0},
        "tests": {"daily": 0, "monthly": 2, "overall": 4864},
        "plans": {"daily": 0, "monthly": 1, "overall": 239},
        "duration": {"builds": 943, "oebuilds": 0, "tests": 449},
    }
    return json.dumps(project).encode("utf-8")


@pytest.fixture
def project_list_json():
    project_list = {
        "count": 1,
        "results": [
            {
                "name": "tuxsuite",
                "builds": {"daily": 0, "monthly": 0, "overall": 1007},
                "oebuilds": {"daily": 0, "monthly": 8, "overall": 31},
                "tests": {"daily": 0, "monthly": 14, "overall": 504},
                "plans": {"daily": 0, "monthly": 2, "overall": 75},
                "duration": {"builds": 0, "oebuilds": 11573, "tests": 1662},
            }
        ],
    }
    return json.dumps(project_list).encode("utf-8")


def test_project_handle_get(
    mocker, project_json, config, response, monkeypatch, tmp_path
):
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "project", "get", "linaro"])
    response.status_code = 200
    response._content = project_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1

    # Test --json
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "project", "get", "linaro", "--json"])
    response.status_code = 200
    response._content = project_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1

    # Test --json-out
    json_path = f"{tmp_path}/project.json"
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "project", "get", "linaro", "--json-out", json_path]
    )
    response.status_code = 200
    response._content = project_json
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


def test_project_handle_list(
    mocker, project_list_json, config, response, monkeypatch, tmp_path
):
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "project", "list"])
    response.status_code = 200
    response._content = project_list_json
    list_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert list_req.call_count == 1

    # Test --json
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "project", "list", "--json"])
    response.status_code = 200
    response._content = project_list_json
    list_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert list_req.call_count == 1

    # Test --json-out
    json_path = f"{tmp_path}/project.json"
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "project", "list", "--json-out", json_path]
    )
    response.status_code = 200
    response._content = project_list_json
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
