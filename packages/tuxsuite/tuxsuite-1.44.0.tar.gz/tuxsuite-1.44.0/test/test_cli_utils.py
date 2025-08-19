# -*- coding: utf-8 -*-

import pytest
from itertools import chain
import json
from tuxsuite.cli.utils import (
    datediff,
    file_or_url,
    key_value,
    show_log,
    format_plan_result,
    load_plan,
    yaml_load,
    load_build_definition,
)
from tuxsuite import Plan
from tuxsuite.cli.yaml import yaml_dump


def test_datediff():
    assert datediff("hello", "hello") == "hello"
    assert datediff("hello world", "hello monde") == "hello monde"


def test_key_value(mocker):
    error = mocker.patch("tuxsuite.cli.utils.error", side_effect=Exception)
    assert key_value("HELLO=WORLD") == ("HELLO", "WORLD")
    assert key_value("HELLO=WORLD=1") == ("HELLO", "WORLD=1")

    with pytest.raises(Exception):
        key_value("HELLO world")
    error.assert_called_once_with("Key Value pair not valid: HELLO world")


def test_file_or_url():
    url = "http://www.example.com/"
    result = file_or_url(url)
    assert result == url

    with pytest.raises(SystemExit):
        file_or_url("/temp/unknown")


def test_show_log(mocker, build):
    mocker.patch("tuxsuite.build.Build.get_status", return_value={"download_url": ""})
    mocker.patch("tuxsuite.build.Build.warnings_count", return_value=1)
    with pytest.raises(SystemExit):
        show_log(build, False, None)


def test_format_plan_result(config, capsys):
    plan_obj = Plan("")

    def get_plan():
        return {
            "builds": {
                "2KgXpq96Y4bh06h3Zd4vvgUZfiP": {
                    "project": "tuxsuite/alok",
                    "uid": "2KgXpq96Y4bh06h3Zd4vvgUZfiP",
                    "plan": "2KgXpWIVjTZew6qAzDH47PuzkTG",
                    "build_name": "kernel builds",
                    "git_repo": "git://test_repo",
                    "git_ref": "master",
                    "kconfig": "test-config",
                    "target_arch": "x86_64",
                    "toolchain": "gcc-8",
                    "state": "finished",
                    "result": "canceled",
                    "build_status": "canceled",
                    "tuxbuild_status": "canceled",
                    "status_message": "Build canceled on request",
                },
                "2KgXplER4lGN5hvUhT5HMuH3lbq": {
                    "project": "tuxsuite/alok",
                    "uid": "2KgXplER4lGN5hvUhT5HMuH3lbq",
                    "plan": "2KgXpWIVjTZew6qAzDH47PuzkTG",
                    "build_name": "",
                    "git_repo": "git://test_repo",
                    "git_ref": "master",
                    "kconfig": "test-config",
                    "target_arch": "x86_64",
                    "toolchain": "gcc-9",
                    "state": "finished",
                    "result": "unknown",
                    "build_status": "unknown",
                    "tuxbuild_status": "unknown",
                },
            },
            "tests": {},
        }

    plan_obj.load(get_plan())
    for b in chain(plan_obj.canceled(), plan_obj.unknown()):
        format_plan_result(b, plan_obj._tests_wait_for(b.uid))
    out, err = capsys.readouterr()
    assert err == ""
    assert (
        out
        == "2KgXpq96Y4bh06h3Zd4vvgUZfiP ⚠️  Canceled with toolchain: gcc-8 target_arch: x86_64\n\
2KgXplER4lGN5hvUhT5HMuH3lbq 🧐 Unknown with toolchain: gcc-9 target_arch: x86_64\n"
    )


def test_load_plan(sample_plan_config, plan_config, get, response, capsys, tmp_path):
    # case: plan file is URL - 200 response
    plan_file = "https://storage.tuxsuite.com/grp/test/project/test/uid/tux_plan.yaml"
    response._content = sample_plan_config.encode("utf-8")
    data = load_plan(plan_file)
    assert data == yaml_load(sample_plan_config, True)

    # case: plan file is URL - 400 response
    plan_file = "https://storage.tuxsuite.com/grp/test/project/test/uid/tux_plan.yaml"
    response.status_code = 400
    response._content = b'{"error": "file not found"}'
    with pytest.raises(SystemExit):
        load_plan(plan_file)
    _, err = capsys.readouterr()
    assert err == 'Error: Failed to get plan file: {"error": "file not found"}\n'

    # case: plan file is Path file
    plan_file = plan_config
    data = load_plan(plan_file)
    assert data == yaml_load(sample_plan_config, True)

    # case: plan file is non existent Path file
    plan_file = "/tmp/not/exist/plan.yaml"
    with pytest.raises(SystemExit):
        load_plan(plan_file)
    _, err = capsys.readouterr()
    assert (
        err
        == "Error: [Errno 2] No such file or directory: '/tmp/not/exist/plan.yaml'\n"
    )

    # case: Invalid yaml plan file
    invalid_yaml = """
key1: value1
key3:
  - item1
  key4:
    subkey2: subvalue2
"""
    plan_file = tmp_path / "invalid-plan.yaml"
    plan_file.write_text(invalid_yaml)
    with pytest.raises(SystemExit):
        load_plan(plan_file)
    _, err = capsys.readouterr()
    assert err is not None

    # case: plan file with invalid plan schema
    plan = """
version: 1
name: Simple plan
description: A simple plan
job:
- name: tinyconfig
  test: {device: qemu-i386, tests: [ltp-smoke]}
"""
    plan_file = tmp_path / "invalid-plan.yaml"
    plan_file.write_text(plan)
    with pytest.raises(SystemExit):
        load_plan(plan_file)
    _, err = capsys.readouterr()
    assert err == "Error: required key not provided @ data['jobs']\n"


def test_load_build_definition(get, response, capsys, tmp_path):
    # YAML format build definition checks

    # case: build definition URL: 200 response
    definition_file = (
        "https://storage.tuxsuite.com/grp/test/project/test/uid/build-definition.yaml"
    )
    content = {"sources": {"repo": {}}}
    response._content = yaml_dump(content).encode("utf-8")
    data = load_build_definition(definition_file)
    assert data == content
    out, _ = capsys.readouterr()
    assert out == ""

    # case: build definition URL: 400 response
    definition_file = (
        "https://storage.tuxsuite.com/grp/test/project/test/uid/build-definition.yaml"
    )
    response.status_code = 400
    response._content = {}
    with pytest.raises(SystemExit):
        load_build_definition(definition_file)

    # case: build definition file path
    definition_file = tmp_path / "build-definition.yaml"
    with open(definition_file, "w") as f:
        yaml_dump(content, f)
    data = load_build_definition(definition_file)
    assert data == content
    out, _ = capsys.readouterr()
    assert out == ""

    # JSON format build definition checks

    # case: build definition URL: 200 response
    definition_file = (
        "https://storage.tuxsuite.com/grp/test/project/test/uid/build-definition.json"
    )
    content = {"sources": {"repo": {}}}
    response.status_code = 200
    response._content = json.dumps(content).encode("utf-8")
    with pytest.raises(SystemExit):
        load_build_definition(definition_file)
    _, err = capsys.readouterr()
    assert "The build definition file is not valid. It must be in YAML format" in err

    # case: build definition URL: 400 response
    definition_file = (
        "https://storage.tuxsuite.com/grp/test/project/test/uid/build-definition.json"
    )
    response.status_code = 400
    response._content = {}
    with pytest.raises(SystemExit):
        load_build_definition(definition_file)

    # case: build definition file path
    definition_file = tmp_path / "build-definition.json"
    with open(definition_file, "w") as f:
        json.dump(content, f)
    with pytest.raises(SystemExit):
        load_build_definition(definition_file)
    _, err = capsys.readouterr()
    assert "The build definition file is not valid. It must be in YAML format" in err
