# Open Embedded plan

A plan is a combination of builds and tests, but OE currently supports only builds.
The combination of builds can be defined in a yaml file consisting of bake build/builds.

!!! note
    The yaml file containing a combination of builds will be referred to as a plan file.

## Kinds of build supported by OE

- Android (kernel / userspace)
- Kas
- OpenEmbedded
- OpenBMC

## Plan configuration

The following plan file consists of all available kinds of builds along with their respective definitions:

### plan.yaml

```yaml
version: 1
name: OEBUILD Examples
description: Build and test TS and LRP
jobs:
- name: Kas Builds
  bakes:
    - sources:
        kas:
          url: "https://git.codelinaro.org/linaro/dependable-boot/meta-ts.git"
          yaml: "ci/qemuarm64-secureboot.yml"
    - sources:
        kas:
          url: "https://git.codelinaro.org/linaro/dependable-boot/meta-ts.git"
          yaml: "ci/rockpi4b.yml"

- name: OE (Repo) builds
  bakes:
    - container: "ubuntu-20.04"
      distro: "rpb"
      envsetup: "setup-environment"
      machine: "ledge-multi-armv8"
      sources:
        repo:
          branch: "master"
          manifest: "default.xml"
          url: "https://github.com/Linaro/ledge-oe-manifest.git"
      target: "ledge-gateway"
    - container: "ubuntu-20.04"
      distro: "rpb"
      envsetup: "setup-environment"
      machine: "ledge-multi-armv8"
      sources:
        repo:
          branch: "master"
          manifest: "default.xml"
          url: "https://github.com/Linaro/ledge-oe-manifest.git"
      target: "ledge-iot"

- name: OE (Git_trees) builds
  bake:
    sources:
      git_trees:
      - url: http://git.yoctoproject.org/git/poky
        branch: honister
      - url: https://github.com/ndechesne/meta-qcom
        branch: honister
    container: ubuntu-20.04
    envsetup: poky/oe-init-build-env
    distro: poky
    machine: dragonboard-845c
    target: core-image-minimal
    bblayers_conf:
    - BBLAYERS += "../meta-qcom/"
    artifacts:
    - "$DEPLOY_DIR"
    environment: {}

- name: Android kernel builds
  bake:
    artifacts: []
    bblayers_conf: []
    container: ubuntu-20.04
    distro:
    environment: {}
    envsetup:
    local_conf: []
    machine:
    name: ''
    sources:
      android:
        branch: common-android-mainline
        build_config: common/build.config.gki.aarch64
        manifest: default.xml
        url: https://android.googlesource.com/kernel/manifest
    targets: null

- name: Android userspace builds
  bake:
    artifacts: []
    bblayers_conf: []
    container: ubuntu-20.04
    distro:
    environment: {}
    envsetup:
    local_conf: []
    machine:
    name: ''
    sources:
      android:
        branch: main
        manifest: default.xml
        url: https://android.googlesource.com/platform/manifest
        lunch_target: db845c
        build_type: user
    targets: null

- name: OpenBMC builds
  bake:
    artifacts: []
    bblayers_conf: []
    container: ubuntu-18.04
    distro: openbmc-romulus
    environment: {}
    envsetup: setup
    local_conf: []
    machine: romulus
    name: ''
    sources:
      git_trees:
        - branch: master
          url: https://github.com/openbmc/openbmc
    targets:
      - obmc-phosphor-image

```

To submit a bake plan, use the following command:

```shell
tuxsuite plan plan.yaml
```
