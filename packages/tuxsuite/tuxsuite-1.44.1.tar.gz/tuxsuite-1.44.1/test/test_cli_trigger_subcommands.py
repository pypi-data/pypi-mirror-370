# -*- coding: utf-8 -*-
import os
import sys
import pytest
import json
import tuxsuite


def test_validate_schema():
    from tuxsuite.cli.trigger import validate_schema

    # Config checks
    # 1) empty config
    with pytest.raises(Exception) as e:
        validate_schema({}, "config")
    assert "required key not provided @ data['repositories']" in str(e.value)
    # 2) check with dict repositories
    with pytest.raises(Exception) as e:
        validate_schema({"repositories": {}}, "config")
    assert "expected a list for dictionary value @ data['repositories']" in str(e.value)
    # 3) check with  list repositories
    validate_schema({"repositories": []}, "config")
    # 4) missing required parameters ( squad_group or url )
    with pytest.raises(Exception) as e:
        validate_schema({"repositories": [{}]}, "config")
    assert "required key not provided @ data['repositories'][0]" in str(e.value)
    # 5) with both squad_group and url required parameter
    validate_schema(
        {"repositories": [{"squad_group": "~alok.ranjan", "url": "https://trst/url"}]},
        "config",
    )
    # 6) Invalid url
    with pytest.raises(Exception) as e:
        validate_schema(
            {"repositories": [{"squad_group": "~alok.ranjan", "url": "test"}]}, "config"
        )
    assert (
        "expected a URL for dictionary value @ data['repositories'][0]['url']"
        in str(e.value)
    )
    # 7) With empty branches
    validate_schema(
        {
            "repositories": [
                {
                    "squad_group": "~alok.ranjan",
                    "url": "https://test.com",
                    "branches": [],
                }
            ]
        },
        "config",
    )
    # 8) missing required parameter 'plan' in branches
    with pytest.raises(Exception) as e:
        validate_schema(
            {
                "repositories": [
                    {
                        "squad_group": "~alok.ranjan",
                        "url": "https://test.com",
                        "branches": [{"name": "tuxtrigger"}],
                    }
                ]
            },
            "config",
        )
    assert (
        "required key not provided @ data['repositories'][0]['branches'][0]['plan']"
        in str(e.value)
    )
    # 8) missing required parameter 'name' in branches
    with pytest.raises(Exception) as e:
        validate_schema(
            {
                "repositories": [
                    {
                        "squad_group": "~alok.ranjan",
                        "url": "https://test.com",
                        "branches": [{"plan": "test-plan"}],
                    }
                ]
            },
            "config",
        )
    assert (
        "required key not provided @ data['repositories'][0]['branches'][0]['name']"
        in str(e.value)
    )

    # plan file check
    # 1) without jobs
    with pytest.raises(Exception) as e:
        validate_schema(
            {"version": 1},
            "plan",
        )
    assert "required key not provided @ data['jobs']" in str(e.value)
    # 2) without version
    with pytest.raises(Exception) as e:
        validate_schema(
            {"jobs": []},
            "plan",
        )
    assert "required key not provided @ data['version']" in str(e.value)


def test_load_yaml(plan_config, sample_plan_config, capsys):
    from tuxsuite.cli.trigger import load_yaml

    # try to load a yaml file
    _, data = load_yaml(plan_config, "plan")

    assert data == open(plan_config).read()

    # FileNotFoundError
    with pytest.raises(SystemExit):
        load_yaml("/tmp/path/test", "config")
    _, error = capsys.readouterr()
    assert "Error: Invalid config file" in error

    # Yaml exception
    yaml_string = """
    name: test yaml
    - invalid_entry
    """
    plan_config.write_text(yaml_string)
    with pytest.raises(SystemExit):
        load_yaml(plan_config, "plan")
    _, error = capsys.readouterr()
    assert "Error: Invalid plan file" in error


def test_trigger_handle_add(
    mocker, config, response, monkeypatch, capsys, plan_config, tuxtrigger_config
):
    # without config and plan
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "trigger", "add"])
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()

    output, error = capsys.readouterr()
    assert "Either config or plan must be provided" in error
    assert exc_info.value.code == 1

    # happy flow with config only
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "trigger",
            "add",
            "--config",
            str(tuxtrigger_config),
        ],
    )
    response.status_code = 201
    response._content = json.dumps({}).encode("utf-8")
    post_req = mocker.patch("requests.post", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "Tuxtrigger 'config/plan' files added\n" == output
    assert post_req.call_count == 1
    assert exc_info.value.code == 0

    # happy flow with plan only
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "trigger",
            "add",
            "--plan",
            str(plan_config),
        ],
    )
    response.status_code = 201
    response._content = json.dumps({}).encode("utf-8")
    post_req = mocker.patch("requests.post", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "Tuxtrigger 'config/plan' files added\n" == output
    assert post_req.call_count == 1
    assert exc_info.value.code == 0

    # happy flow with plan directory
    plan_dir = os.path.dirname(str(plan_config))
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "trigger",
            "add",
            "--plan",
            plan_dir,
        ],
    )
    response.status_code = 201
    response._content = json.dumps({}).encode("utf-8")
    post_req = mocker.patch("requests.post", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "Tuxtrigger 'config/plan' files added\n" == output
    assert post_req.call_count == 1
    assert exc_info.value.code == 0

    # failed request
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "trigger",
            "add",
            "--config",
            str(tuxtrigger_config),
            "--plan",
            str(plan_config),
        ],
    )
    response.status_code = 400
    response._content = json.dumps({}).encode("utf-8")
    post_req = mocker.patch("requests.post", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "Error: Failed to add tuxtrigger 'config/plan'.\n" == error
    assert post_req.call_count == 1
    assert exc_info.value.code == 1


def test_trigger_handle_delete(
    mocker, plan_config, config, response, monkeypatch, capsys
):
    # without config and plan
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "trigger", "delete"])
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()

    output, error = capsys.readouterr()
    assert "Either config or plan must be provided for deletion" in error
    assert exc_info.value.code == 1

    # happy flow with config only
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "trigger",
            "delete",
            "--config",
        ],
    )
    response.status_code = 200
    response._content = {}
    post_req = mocker.patch("requests.delete", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "Config: config.yaml file deleted\n" == output
    assert post_req.call_count == 1
    assert exc_info.value.code == 0

    # happy flow with plan only
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "trigger",
            "delete",
            "--plan",
            "test-plan-1",
            "--plan",
            "test-plan-2",
        ],
    )
    response.status_code = 200
    response._content = {}
    post_req = mocker.patch("requests.delete", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "Plan: test-plan-1,test-plan-2 file deleted\n" == output
    assert post_req.call_count == 1
    assert exc_info.value.code == 0

    # happy flow with config and plan
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "trigger",
            "delete",
            "--config",
            "--plan",
            "test-plan",
        ],
    )
    response.status_code = 200
    response._content = {}
    post_req = mocker.patch("requests.delete", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "Config: config.yaml Plan: test-plan file deleted\n" == output
    assert post_req.call_count == 1
    assert exc_info.value.code == 0

    # failed request
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "trigger",
            "delete",
            "--config",
            "--plan",
            "planv1.yaml",
        ],
    )
    response.status_code = 400
    response._content = {}
    post_req = mocker.patch("requests.delete", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert (
        "Error: Failed to delete Config: config.yaml Plan: planv1.yaml file\n" == error
    )
    assert post_req.call_count == 1
    assert exc_info.value.code == 1


def test_trigger_handle_get(
    mocker, sample_plan_config, config, response, monkeypatch, capsys
):
    # without config and plan
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "trigger", "get"])
    response.status_code = 200
    ret = {"config": "config.yaml", "plans": ["plan1", "plan2"]}
    response._content = json.dumps(ret).encode("utf-8")
    get_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "Tuxtrigger config:" in output
    assert exc_info.value.code == 0
    assert get_req.call_count == 1

    # with config
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "trigger", "get", "--config"])
    response.status_code = 200
    ret = {"config": sample_plan_config}
    response._content = json.dumps(ret).encode("utf-8")
    get_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "version: 1" in output
    assert exc_info.value.code == 0
    assert get_req.call_count == 1

    # with plan
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "trigger", "get", "--plan", "test-plan"]
    )
    response.status_code = 200
    ret = {"plan": sample_plan_config}
    response._content = json.dumps(ret).encode("utf-8")
    get_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "version: 1" in output
    assert exc_info.value.code == 0
    assert get_req.call_count == 1

    # with config and plan
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "trigger", "get", "--config", "--plan", "test-plan"],
    )
    response.status_code = 200
    ret = {"config": "config.yaml", "plans": ["plan1", "plan2"]}
    response._content = json.dumps(ret).encode("utf-8")
    get_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "--plan: not allowed with argument --config" in error
    assert exc_info.value.code == 2
    assert get_req.call_count == 0

    # Test failure case when the response is not 200
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "trigger", "get"])
    response.status_code = 400
    response._content = {}
    get_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    assert get_req.call_count == 1
    assert exc_info.value.code == 1
    output, error = capsys.readouterr()
    assert (
        "Error: Failed to get the tuxtrigger config/plan. Is config/plan exists! ?\n"
        == error
    )
