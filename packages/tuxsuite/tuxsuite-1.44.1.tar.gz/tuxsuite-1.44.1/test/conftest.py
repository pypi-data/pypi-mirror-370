# -*- coding: utf-8 -*-

import os
import requests
import tarfile
import tuxsuite.config
import pytest


@pytest.fixture(autouse=True)
def session(mocker):
    mocker.patch("requests.Session.get")
    mocker.patch("requests.Session.post")
    return requests.Session


@pytest.fixture
def response():
    r = requests.Response()
    r.status_code = 200
    return r


@pytest.fixture
def post(session, response):
    session.post.return_value = response
    return session.post


@pytest.fixture
def get(session, response):
    session.get.return_value = response
    return session.get


@pytest.fixture
def tuxauth(mocker):
    get = mocker.Mock(
        return_value=mocker.Mock(
            **{
                "status_code": 200,
                "json.return_value": {
                    "UserDetails": {"Groups": ["tuxsuite"], "Name": "tux"}
                },
            }
        )
    )
    mocker.patch("tuxsuite.config.requests.get", get)
    return get


@pytest.fixture
def sample_token():
    return "Q9qMlmkjkIuIGmEAw-Mf53i_qoJ8Z2eGYCmrNx16ZLLQGrXAHRiN2ce5DGlAebOmnJFp9Ggcq9l6quZdDTtrkw"


@pytest.fixture
def sample_url():
    return "https://foo.bar.tuxbuild.com/v1"


@pytest.fixture(autouse=True)
def home(monkeypatch, tmp_path):
    h = tmp_path / "HOME"
    h.mkdir()
    monkeypatch.setenv("HOME", str(h))
    return h


@pytest.fixture
def config(monkeypatch, sample_token, sample_url, tuxauth):
    monkeypatch.setenv("TUXSUITE_TOKEN", sample_token)
    monkeypatch.setenv("TUXSUITE_URL", sample_url)
    config = tuxsuite.config.Config("/nonexistent")
    config.kbapi_url = sample_url
    config.auth_token = sample_token
    config.token = sample_token
    return config


@pytest.fixture
def sample_plan_config():
    return """
version: 1
name: Simple plan
description: A simple plan
jobs:

- name: simple-gcc
  build: {toolchain: gcc-8, target_arch: i386, kconfig: tinyconfig}
  test: {device: qemu-i386, tests: [ltp-smoke], rootfs: "https://example.com/rootfs.ext4.zst"}

- name: full-gcc
  builds:
    - {toolchain: gcc-8, target_arch: i386, kconfig: tinyconfig}
    - {toolchain: gcc-9, target_arch: i386, kconfig: tinyconfig}
    - {toolchain: gcc-10, target_arch: i386, kconfig: tinyconfig}
  test: {device: qemu-i386, tests: [ltp-smoke], overlay:[[overlay.tgz,/tmp],[overlay2.tgz]]}

- builds:
    - {toolchain: clang-10, target_arch: i386, kconfig: tinyconfig}
    - {toolchain: clang-11, target_arch: i386, kconfig: tinyconfig}
    - {toolchain: clang-nightly, target_arch: i386, kconfig: tinyconfig}
  test: {device: qemu-i386, overlay: overlay.tgz}

- build: {toolchain: clang-nightly, target_arch: i386, kconfig: tinyconfig}
  tests:
    - {device: qemu-i386}
    - {device: qemu-i386, tests: [ltp-smoke]}

- builds:
    - {toolchain: gcc-8, target_arch: i386, kconfig: tinyconfig}
    - {toolchain: gcc-9, target_arch: i386, kconfig: tinyconfig}
    - {toolchain: gcc-10, target_arch: i386, kconfig: tinyconfig}
  tests:
    - {device: qemu-i386, parameters: {HELLO: WORLD}}
    - {device: qemu-i386, tests: [ltp-syscalls], sharding: 3}
    - {device: qemu-i386, tests: [ltp-commands], sharding: 1, parameters: {HELLO: WORLD}}

- tests:
    - {kernel: https://storage.tuxboot.com/arm64/Image, device: qemu-arm64, tests: [ltp-smoke]}
    - {kernel: https://storage.tuxboot.com/i386/bzImage, device: qemu-i386, tests: [ltp-smoke]}
    - {kernel: https://storage.tuxboot.com/mips64/vmlinux, device: qemu-mips64, tests: [ltp-smoke]}
    - {kernel: https://storage.tuxboot.com/ppc64/vmlinux, device: qemu-ppc64, tests: [ltp-smoke]}
    - kernel: https://storage.tuxboot.com/riscv64/Image
      device: qemu-riscv64
      bios: https://storage.tuxboot.com/riscv64/fw_jump.elf
      tests: [ltp-smoke]
    - kernel: https://storage.tuxboot.com/x86_64/bzImage
      device: qemu-x86_64
      rootfs: https://storage.tuxboot.com/x86_64/rootfs.ext4.zst
      tests: [ltp-smoke]
"""


@pytest.fixture
def plan_config(tmp_path, sample_plan_config):
    c = tmp_path / "planv1.yml"
    c.write_text(sample_plan_config)
    return c


@pytest.fixture
def sample_plan_with_sanity():
    return """
version: 1
name: Simple sanity plan
description: A simple sanity plan
jobs:
- build: {toolchain: clang-nightly, target_arch: i386, kconfig: tinyconfig}
  sanity_test: {device: qemu-i386}
  tests:
    - {device: qemu-i386}
    - {device: qemu-i386, tests: [ltp-smoke]}

- builds:
    - {toolchain: gcc-8, target_arch: i386, kconfig: tinyconfig}
    - {toolchain: gcc-9, target_arch: i386, kconfig: tinyconfig}
    - {toolchain: gcc-10, target_arch: i386, kconfig: tinyconfig}
  sanity_test: {device: qemu-i386, parameters: {HELLO: WORLD}}
  tests:
    - {device: qemu-i386, parameters: {HELLO: WORLD}}
    - {device: qemu-i386, tests: [ltp-syscalls], sharding: 3}
    - {device: qemu-i386, tests: [ltp-commands], sharding: 1, parameters: {HELLO: WORLD}}
- build: {toolchain: clang-nightly, target_arch: i386, kconfig: tinyconfig}
  tests:
    - {device: qemu-i386}
    - {device: qemu-i386, tests: [ltp-smoke]}

- tests:
    - {kernel: https://storage.tuxboot.com/arm64/Image, device: qemu-arm64, tests: [ltp-smoke]}
    - {kernel: https://storage.tuxboot.com/i386/bzImage, device: qemu-i386, tests: [ltp-smoke]}
    - {kernel: https://storage.tuxboot.com/mips64/vmlinux, device: qemu-mips64, tests: [ltp-smoke]}
    - {kernel: https://storage.tuxboot.com/ppc64/vmlinux, device: qemu-ppc64, tests: [ltp-smoke]}
    - kernel: https://storage.tuxboot.com/riscv64/Image
      device: qemu-riscv64
      bios: https://storage.tuxboot.com/riscv64/fw_jump.elf
      tests: [ltp-smoke]
    - kernel: https://storage.tuxboot.com/x86_64/bzImage
      device: qemu-x86_64
      rootfs: https://storage.tuxboot.com/x86_64/rootfs.ext4.zst
      tests: [ltp-smoke]
  sanity_test: {kernel: https://storage.tuxboot.com/arm64/Image, device: qemu-arm64, tests: [ltp-smoke]}
- tests:
    - {kernel: https://storage.tuxboot.com/arm64/Image, device: qemu-arm64, tests: [ltp-smoke]}
    - {kernel: https://storage.tuxboot.com/i386/bzImage, device: qemu-i386, tests: [ltp-smoke]}
"""


@pytest.fixture
def sanity_plan_config(tmp_path, sample_plan_with_sanity):
    c = tmp_path / "sanity_plan.yml"
    c.write_text(sample_plan_with_sanity)
    return c


@pytest.fixture
def sample_tuxtrigger_config():
    return """
repositories:
- url: https://some/test/repo/url
  squad_group: ~first_name.lastname
  branches:
  - name: test_branch
    plan: test_plan.yaml
"""


@pytest.fixture
def tuxtrigger_config(tmp_path, sample_tuxtrigger_config):
    c = tmp_path / "config.yml"
    c.write_text(sample_tuxtrigger_config)
    return c


@pytest.fixture
def sample_bake_plan_config():
    return """
common: &commondata
  "container": "ubuntu-20.04"
  "distro": "rpb"
  "envsetup": "setup-environment"
  "machine": "dragonboard-845c"
  "sources": {
    "repo": {
      "branch": "qcom/dunfell",
      "manifest": "default.xml",
      "url": "https://github.com/96boards/oe-rpb-manifest.git",
    }
  }
  "target": "rpb-console-image rpb-console-image-test rpb-desktop-image rpb-desktop-image-test"
version: 1
name: armv7 validation
description: Build and test linux kernel for armv7
jobs:
- name: armv7
  bake: { <<: *commondata, "machine": "ledge-multi-armv7"}

- name: lt-qcom
  bakes:
    - { <<: *commondata}
    - { <<: *commondata}
"""


@pytest.fixture
def bake_plan_config(tmp_path, sample_bake_plan_config):
    bake_config = tmp_path / "sample_bake_plan.yml"
    bake_config.write_text(sample_bake_plan_config)
    return bake_config


@pytest.fixture
def sample_bake_plan_extended_config():
    return """
name: OE RPB tux CI test (LTS)
description: A sanity test for OE RPB
version: 1

common: &commondata
  container: ubuntu-20.04
  envsetup: setup-environment
  sources:
    repo:
      branch: qcom/dunfell
      manifest: default.xml
      url: https://github.com/96boards/oe-rpb-manifest.git
  local_conf:
    - INHERIT += 'buildstats buildstats-summary'
    - INHERIT:remove = 'rm_work'
  artifacts:
    - $DEPLOY_DIR

rpb: &rpb
  distro: rpb
  target: rpb-console-image

rpb-wayland: &rpb-wayland
  distro: rpb-wayland
  target: rpb-console-image

jobs:
- name: rpb
  bakes:
    - { <<: [*commondata, *rpb], machine: dragonboard-410c, name: dragonboard-410c-rpb }
    - { <<: [*commondata, *rpb], machine: dragonboard-845c, name: dragonboard-845c-rpb }
- name: rpb-wayland
  bakes:
    - { <<: [*commondata, *rpb-wayland], machine: dragonboard-410c, name: dragonboard-410c-rpb-wayland }
    - { <<: [*commondata, *rpb-wayland], machine: dragonboard-845c, name: dragonboard-845c-rpb-wayland }

"""


@pytest.fixture
def bake_plan_extended_config(tmp_path, sample_bake_plan_extended_config):
    bake_config = tmp_path / "sample_bake_plan.yml"
    bake_config.write_text(sample_bake_plan_extended_config)
    return bake_config


@pytest.fixture
def sample_bake_plan_config_with_test():
    return """
common: &commondata
  "container": "ubuntu-20.04"
  "distro": "rpb"
  "envsetup": "setup-environment"
  "machine": "dragonboard-845c"
  "sources": {
    "repo": {
      "branch": "qcom/dunfell",
      "manifest": "default.xml",
      "url": "https://github.com/96boards/oe-rpb-manifest.git",
    }
  }
  "target": "rpb-console-image rpb-console-image-test rpb-desktop-image rpb-desktop-image-test"
version: 1
name: armv7 validation
description: Build and test linux kernel for armv7
jobs:
- name: armv7
  bake: { <<: *commondata, "machine": "ledge-multi-armv7"}

- name: lt-qcom
  bakes:
    - { <<: *commondata}
    - { <<: *commondata}
  tests:
    - {device: qemu-i386}
    - {device: qemu-i386, tests: [ltp-smoke]}
"""


@pytest.fixture
def bake_plan_config_with_test(tmp_path, sample_bake_plan_config_with_test):
    bake_config = tmp_path / "sample_bake_plan.yml"
    bake_config.write_text(sample_bake_plan_config_with_test)
    return bake_config


@pytest.fixture
def sample_plan_unknown_version():
    return """
version: -1
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
def plan_config_unknown_version(tmp_path, sample_plan_unknown_version):
    config = tmp_path / "plan.yaml"
    with config.open("w") as f:
        f.write(sample_plan_unknown_version)
    return config


@pytest.fixture
def sample_patch():
    return "example mbox patch"


@pytest.fixture
def sample_patch_file(tmp_path, sample_patch):
    p = tmp_path / "patch.mbox"
    p.write_text(sample_patch)
    return str(p)


@pytest.fixture
def sample_patch_dir(tmp_path, sample_patch):
    p = tmp_path / "patch.mbox"
    p.write_text(sample_patch)
    s = tmp_path / "series"
    s.write_text("mock series file")
    return str(tmp_path)


@pytest.fixture
def sample_patch_tgz(tmp_path, sample_patch, sample_patch_dir):
    p = tmp_path / "patch.mbox"
    p.write_text(sample_patch)
    s = tmp_path / "series"
    s.write_text("mock series file")
    tar_file = os.path.join(tmp_path, "patch.tgz")
    with tarfile.open(tar_file, "w:gz") as tar:
        tar.add(tmp_path, arcname=os.path.sep)
    return str(tar_file)


@pytest.fixture
def sample_patch_tgz_no_series(tmp_path, sample_patch, sample_patch_dir):
    p = tmp_path / "patch.mbox"
    p.write_text(sample_patch)
    s = tmp_path / "series"
    os.remove(s)
    tar_file = os.path.join(tmp_path, "no_series_patch.tgz")
    with tarfile.open(tar_file, "w:gz") as tar:
        tar.add(tmp_path, arcname=os.path.sep)
    return str(tar_file)


@pytest.fixture
def sample_patch_mbx(tmp_path, sample_patch, sample_patch_dir):
    p = tmp_path / "patch.mbx"
    p.write_text(sample_patch)
    return str(p)


@pytest.fixture
def sample_manifest():
    return '<?xml version="1.0" encoding="UTF-8"?><manifest></manifest>'


@pytest.fixture
def sample_manifest_file(tmp_path, sample_manifest):
    m = tmp_path / "default.xml"
    m.write_text(sample_manifest)
    return str(m)


@pytest.fixture
def build_attrs():
    return {
        "group": "tuxsuite",
        "project": "unittests",
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


@pytest.fixture
def build(build_attrs):
    b = tuxsuite.build.Build(**build_attrs)
    b.uid = "myuid"
    return b


@pytest.fixture
def single_build_plan():
    return """
version: 1
name: Simple sanity plan
description: A simple sanity plan
jobs:
- build: {toolchain: clang-nightly, target_arch: i386, kconfig: tinyconfig}
"""


@pytest.fixture
def build_plan(tmp_path, single_build_plan):
    m = tmp_path / "build-plan.yaml"
    m.write_text(single_build_plan)
    return str(m)


@pytest.fixture
def single_test_plan():
    return """
version: 1
name: Simple sanity plan
description: A simple sanity plan
jobs:
- test:
    device: qemu-i386
    tests: [ltp-smoke]
    dtb: https://storage.tuxsuite.com/grp/prj/tests/uid/dtbs/am57xx-beagle-x15.dtb
    parameters:
      ITERATIONS: 2
      SKIPFILE: skipfile-lkft.yaml
      KSELFTEST: https://storage.tuxsuite.com/grp/prj/tests/uid/kselftest.tar.xz
      PERF: https://storage.tuxsuite.com/grp/prj/tests/uid/perf.tar.xz
"""


@pytest.fixture
def test_plan(tmp_path, single_test_plan):
    m = tmp_path / "test-plan.yaml"
    m.write_text(single_test_plan)
    return str(m)
