# Example

## Android Plan

!!! info "Android Plan"
    Android plan file containing single build in bake and multiple builds in bakes

``` yaml
version: 1
name: Android Plan Example
description: Android example description
jobs:
- name: single android kernel build using bake
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

- name: single android userspace build using bake
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

- name: Multiple builds using bakes
  bakes:
  - artifacts: []
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
  - artifacts: []
    bblayers_conf: []
    container: ubuntu-20.04
    distro: null
    environment: {}
    envsetup: null
    local_conf: []
    machine: null
    name: ''
    sources:
     android:
      bazel: true
      branch: common-android14-5.15
      build_config: //common:db845c_dist
      manifest: default.xml
      url: https://android.googlesource.com/kernel/manifest
    targets: null
  - artifacts: []
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

```

## Kas Plan

!!! info "Kas Plan"
    Kas plan file containing single build in bake and multiple builds in bakes

``` yaml
version: 1
name: Kas Plan Example
description: Kas example description
jobs:
- name: single
  bake:
    sources:
      kas:
        url: "https://git.codelinaro.org/linaro/dependable-boot/meta-ts.git"
        yaml: "ci/qemuarm64-secureboot.yml"

- name: multiple
  bakes:
    - sources:
        kas:
          url: "https://git.codelinaro.org/linaro/dependable-boot/meta-ts.git"
          yaml: "ci/qemuarm64-secureboot.yml"
    - sources:
        kas:
          url: "https://git.codelinaro.org/linaro/dependable-boot/meta-ts.git"
          yaml: "ci/rockpi4b.yml"

```

!!! tip "Kas plan with kas override file"
  Submit a dependent kas override file for a plan containing kas build/builds.
!!! note "plan.yml"

``` yaml

description: ''
jobs:
- bake:
    name: build-meta-ewaol-machine-avadp
    sources:
      kas:
        branch: kirkstone-dev
        url: https://gitlab.com/soafee/ewaol/meta-ewaol-machine.git
        yaml: kas/ewaol/baremetal.yml:kas/machine/avadp.yml:kas/ewaol/ci-constraints.yml
name: build-meta-ewaol-machine-avadp
version: 1

```

!!! note "kas_override_file.yml"

``` yaml
header:
 version: 11

repos:
 meta-ewaol:
  url: https://gitlab.com/soafee/ewaol/meta-ewaol.git
  refspec: refs/merge-requests/11/merge
  path: layers/meta-ewaol

```

To submit a kas plan with kas override file:

``` shell

tuxsuite plan plan.yml -k kas_override_file.yml

```

## OE Plan

!!! info "OE Plan"
    OE plan file containing single build in bake and multiple builds in bakes

``` yaml
version: 1
name: OE Plan example
description: OE example description
jobs:
- name: OE (Git_trees) builds
  bake:
    sources:
      git_trees:
      - url: http://git.yoctoproject.org/git/poky
        branch: honister
      - url: https://github.com/ndechesne/meta-qcom
        branch: honister
    container: ubuntu-20.04
    extraconfigs: []
    envsetup: poky/oe-init-build-env
    distro: poky
    machine: dragonboard-845c
    target: core-image-minimal
    bblayers_conf:
    - BBLAYERS += "../meta-qcom/"
    artifacts:
    - "$DEPLOY_DIR"
    environment: {}

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
      extraconfigs: []
      envsetup: "setup-environment"
      machine: "ledge-multi-armv8"
      sources:
        repo:
          branch: "master"
          manifest: "default.xml"
          url: "https://github.com/Linaro/ledge-oe-manifest.git"
      target: "ledge-iot"

```

## Openbmc Plan

!!! info "openbmc Plan"
    Openbmc plan file containing single build in bake and multiple builds in bakes

``` yaml
version: 1
name: Openbmc Plan Examples
description: Openbmc example description
jobs:
- name: Openbmc builds
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
- name: Openbmc builds
  bakes:
    - artifacts: []
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
    - artifacts: []
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

You can submit the above plan files through tuxsuite cli using the command:

``` shell
tuxsuite plan plan.yaml

```

!!! tip "Tuxsuite usage"

You can also submit only a particular job of a plan file:

``` shell
tuxsuite plan plan.yaml --job-name "job name"
```

This will submit only the builds specified under the given name.

!!! tip "Tuxsuite usage"

A plan can be submitted with manifest as well:

``` shell
tuxsuite plan plan.yaml --local-manifest local-manifest.xml
```
