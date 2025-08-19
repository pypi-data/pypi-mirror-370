# -*- coding: utf-8 -*-

import sys
import json
import pytest
import tuxsuite


@pytest.fixture
def keys_json():
    keys = {
        "ssh": {"pub": "ecdsa-sha2-nistp256 AAAADianw="},
        "pat": [
            {"token": "****", "username": "test-user-2", "domain": "gitlab.com"},
            {"token": "****", "username": "test-user-4", "domain": "github.com"},
        ],
        "variables": [
            {"value": "****", "keyname": "test-key-2", "type": "file"},
            {"value": "****", "keyname": "test-key-4", "type": "variable"},
        ],
    }
    return json.dumps(keys, indent=True).encode("utf-8")


def test_keys_handle_get(
    mocker, keys_json, config, response, monkeypatch, capsys, tmp_path
):
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "keys", "get"])
    response.status_code = 200
    response._content = keys_json
    get_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "ssh public key:" in output
    assert exc_info.value.code == 0
    assert get_req.call_count == 1

    # # Test --json
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "keys", "get", "--json"],
    )
    response.status_code = 200
    response._content = keys_json
    get_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    assert exc_info.value.code == 0
    assert get_req.call_count == 1

    # Test --json-out
    json_path = f"{tmp_path}/keys.json"
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "keys", "get", "--json-out", json_path],
    )
    response.status_code = 200
    response._content = keys_json
    get_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    assert exc_info.value.code == 0
    assert get_req.call_count == 1

    # Test failure case when the response is not 200
    response.status_code = 400
    response._content = {}
    get_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    assert get_req.call_count == 1
    assert exc_info.value.code == 1
    output, error = capsys.readouterr()
    assert "Error: Failed to get the keys\n" == error


def test_keys_handle_add(mocker, keys_json, config, response, monkeypatch, capsys):
    # wrong key type
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "keys", "add", "--type", "unknown-type"]
    )
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "invalid choice: 'unknown-type'" in error

    # without required options with type 'pat'
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "keys", "add", "--type", "pat"])
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "--domain is required for key type 'pat'" in error
    assert exc_info.value.code == 1

    # without required options with type 'variables'
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "keys", "add", "--type", "variables:env"]
    )
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert (
        "missing key value pair, please provide key value in 'KEY=VALUE' format"
        in error
    )
    assert exc_info.value.code == 1

    # without username and domain options for type 'pat'
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "keys", "add", "--type", "pat", "--token", "test-token"],
    )
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "--domain is required for key type 'pat'" in error
    assert exc_info.value.code == 1

    # without value for key type 'variables'
    mocker.resetall()
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "keys", "add", "--type", "variables:file", "KEY"]
    )
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "Key value pair not valid, must be in 'KEY=VALUE' format" in error
    assert exc_info.value.code == 1

    # without domain option for type 'pat'
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "keys",
            "add",
            "--type",
            "pat",
            "--token",
            "test-token",
            "--username",
            "test-user-1",
        ],
    )
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "--domain is required" in error
    assert exc_info.value.code == 1

    # without kind option for type 'variables'
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "keys", "add", "--type", "variables", "KEY=VALUE"],
    )
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "invalid choice: 'variables'" in error
    assert exc_info.value.code == 2

    # happy flow for type 'pat'
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "keys",
            "add",
            "--type",
            "pat",
            "--token",
            "test-token",
            "--username",
            "test-user-1",
            "--domain",
            "gitlab.com",
        ],
    )
    response.status_code = 201
    response._content = {}
    post_req = mocker.patch("requests.post", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "'pat' key 'gitlab.com:test-user-1' added\n" == output
    assert post_req.call_count == 1
    assert exc_info.value.code == 0

    # happy flow for type 'variables'
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "keys", "add", "--type", "variables:file", "KEY=VALUE"],
    )
    response.status_code = 201
    response._content = {}
    post_req = mocker.patch("requests.post", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "'variables' key 'KEY:file' added\n" == output
    assert post_req.call_count == 1
    assert exc_info.value.code == 0

    # failed request for type 'pat'
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "keys",
            "add",
            "--type",
            "pat",
            "--token",
            "test-token",
            "--username",
            "test-user-1",
            "--domain",
            "gitlab.com",
        ],
    )
    response.status_code = 400
    response._content = json.dumps({}).encode("utf-8")
    post_req = mocker.patch("requests.post", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "Error: Failed to add 'pat' key 'gitlab.com:test-user-1'.\n" == error
    assert post_req.call_count == 1
    assert exc_info.value.code == 1

    # failed request for type 'variables'
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "keys", "add", "--type", "variables:env", "KEY=VALUE"],
    )
    response.status_code = 400
    response._content = json.dumps({}).encode("utf-8")
    post_req = mocker.patch("requests.post", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "Error: Failed to add 'variables' key 'KEY:variable'.\n" == error
    assert post_req.call_count == 1
    assert exc_info.value.code == 1


def test_keys_handle_delete(mocker, keys_json, config, response, monkeypatch, capsys):
    # wrong key type
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "keys", "delete", "--type", "unknown-type"]
    )
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()

    # without required options for type 'pat'
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "keys", "delete", "--type", "pat"])
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "--domain is required for key type 'pat'" in error
    assert exc_info.value.code == 1

    # without required options for type 'variables'
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "keys", "delete", "--type", "variables:env"]
    )
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "KEYNAME is required for type variables" in error
    assert exc_info.value.code == 1

    # without required options for type 'pat'
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "keys", "delete", "--type", "pat", "--domain", "gitlab.com"],
    )
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "--username is required for key type 'pat'" in error
    assert exc_info.value.code == 1

    # happy flow for type 'pat'
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "keys",
            "delete",
            "--type",
            "pat",
            "--domain",
            "gitlab.com",
            "--username",
            "test-user-1",
        ],
    )
    response.status_code = 200
    response._content = {}
    delete_req = mocker.patch("requests.delete", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "'pat' key 'gitlab.com:test-user-1' deleted\n" == output
    assert delete_req.call_count == 1
    assert exc_info.value.code == 0

    # happy flow for type 'variables'
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "keys", "delete", "--type", "variables:env", "KEY"],
    )
    response.status_code = 200
    response._content = {}
    delete_req = mocker.patch("requests.delete", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "'variables' key 'KEY' deleted\n" == output
    assert delete_req.call_count == 1
    assert exc_info.value.code == 0

    # failed request for type 'pat'
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "keys",
            "delete",
            "--type",
            "pat",
            "--domain",
            "unknown",
            "--username",
            "test-user-1",
        ],
    )
    response.status_code = 400
    response._content = {}
    delete_req = mocker.patch("requests.delete", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "Error: Failed to delete 'pat' key 'unknown:test-user-1'\n" == error
    assert delete_req.call_count == 1
    assert exc_info.value.code == 1

    # failed request for type 'variables'
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "keys", "delete", "--type", "variables:env", "KEY"],
    )
    response.status_code = 400
    response._content = {}
    delete_req = mocker.patch("requests.delete", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "Error: Failed to delete 'variables' key 'KEY'\n" == error
    assert delete_req.call_count == 1
    assert exc_info.value.code == 1


def test_keys_handle_update(mocker, keys_json, config, response, monkeypatch, capsys):
    # wrong key type
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "keys", "update", "--type", "unknown-type"]
    )
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    assert exc_info.value.code == 2

    # without required options for type 'pat'
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "keys", "update", "--type", "pat"])
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "--domain is required for key type 'pat'" in error
    assert exc_info.value.code == 1

    # without required options for type 'variables'
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "keys", "update", "--type", "variables:env"]
    )
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "" in error
    assert exc_info.value.code == 1

    # without username and domain options for type 'pat'
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "keys", "update", "--type", "pat", "--token", "test-token"],
    )
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "--domain is required for key type 'pat'" in error
    assert exc_info.value.code == 1

    # without keyname for type 'variables'
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "keys", "update", "--type", "variables:env"],
    )
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert (
        "missing key value pair, please provide key value in 'KEY=VALUE' format"
        in error
    )
    assert exc_info.value.code == 1

    # without domain option for type 'pat'
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "keys",
            "update",
            "--type",
            "pat",
            "--token",
            "test-token",
            "--username",
            "test-user-1",
        ],
    )
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "--domain is required for key type 'pat'" in error
    assert exc_info.value.code == 1

    # without kind option for type 'variables'
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "keys", "update", "--type", "variables", "KEY"],
    )
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "invalid choice: 'variables'" in error
    assert exc_info.value.code == 2

    # happy flow for type 'pat'
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "keys",
            "update",
            "--type",
            "pat",
            "--token",
            "test-token",
            "--username",
            "test-user-1",
            "--domain",
            "gitlab.com",
        ],
    )
    response.status_code = 201
    response._content = {}
    put_req = mocker.patch("requests.put", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "'pat' key 'gitlab.com:test-user-1' updated\n" == output
    assert put_req.call_count == 1
    assert exc_info.value.code == 0

    # happy flow for type 'variables'
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "keys", "update", "--type", "variables:file", "KEY=VALUE"],
    )
    response.status_code = 201
    response._content = {}
    put_req = mocker.patch("requests.put", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "'variables' key 'KEY:file' updated\n" == output
    assert put_req.call_count == 1
    assert exc_info.value.code == 0

    # failed request for type 'pat'
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "keys",
            "update",
            "--type",
            "pat",
            "--token",
            "test-token",
            "--username",
            "test-user-1",
            "--domain",
            "gitlab.com",
        ],
    )
    response.status_code = 400
    response._content = {}
    put_req = mocker.patch("requests.put", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "Error: Failed to update 'pat' key 'gitlab.com:test-user-1'\n" == error
    assert put_req.call_count == 1
    assert exc_info.value.code == 1

    # failed request for type 'variables'
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "keys", "update", "--type", "variables:file", "KEY=VALUE"],
    )
    response.status_code = 400
    response._content = {}
    put_req = mocker.patch("requests.put", return_value=response)
    with pytest.raises(SystemExit) as exc_info:
        tuxsuite.cli.main()
    output, error = capsys.readouterr()
    assert "Error: Failed to update 'variables' key 'KEY:file'\n" == error
    assert put_req.call_count == 1
    assert exc_info.value.code == 1
