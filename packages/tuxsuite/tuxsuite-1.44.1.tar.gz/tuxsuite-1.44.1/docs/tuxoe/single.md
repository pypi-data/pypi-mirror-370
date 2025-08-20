# A single OpenEmbedded build

Submit an OE build request using the tuxsuite command line interface. This will
wait for the OE build to complete before returning by default.

```shell
git clone https://gitlab.com/Linaro/tuxsuite
cd tuxsuite
tuxsuite bake submit examples/bitbake/oniro.yaml
```

## OE Versions

Currently TuxOE supports from `dunfell` to `styhead`.

TuxOE allows to build with various ubuntu LTS versions supported by the Yocto Project from `16.04` to `22.04`.

## Build definition

TuxOE uses build definition to describe the build:

* layers to download
* `local.conf` and `bblayers.conf` to use
* machine type
* distro targets
* ...

TuxOE can download the layers using either git protocol or the repo tool.

!!! example "Using repo"

      ```yaml
      container: ubuntu-20.04
      distro: rpb
      envsetup: setup-environment
      machine: dragonboard-845c
      extraconfigs: []
      sources:
        repo:
          branch: qcom/dunfell
          manifest: default.xml
          url: https://github.com/96boards/oe-rpb-manifest.git
      target: rpb-console-image rpb-console-image-test rpb-desktop-image
        rpb-desktop-image-test
      ```

!!! example "Using git repositories"

      ```yaml
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
      environment: {}
      ```

!!! example "Using Android"

      ```yaml
      artifacts: []
      bblayers_conf: []
      container: ubuntu-20.04
      distro: null
      environment: {}
      envsetup: null
      local_conf: []
      machine: null
      name: ""
      sources:
        android:
          branch: common-android11-5.4
          build_config: common/build.config.db845c
          manifest: default.xml
          url: https://android.googlesource.com/kernel/manifest
      targets: null
      ```

!!! example "Using Android userspace"

      ```yaml
      artifacts: []
      bblayers_conf: []
      container: ubuntu-20.04
      distro: null
      environment: {}
      envsetup: null
      local_conf: []
      machine: null
      name: ""
      sources:
        android:
          branch: main
          manifest: default.xml
          url: https://android.googlesource.com/platform/manifest
          lunch_target: db845c
          build_type: user
      targets: null
      ```

!!! example "Using kas"

      ```yaml
      artifacts:
        - baremetal/deploy/images
        - "*/deploy/rpm"
        - "*/*/licenses"
      sources:
        kas:
          branch: kirkstone-dev
          url: https://gitlab.com/soafee/ewaol/meta-ewaol-machine.git
          yaml: kas/ewaol/baremetal.yml:kas/machine/avadp.yml:kas/ewaol/ci-constraints.yml:kas/ewaol/tests.yml
      ```

!!! example "kas build with a dependent kas override file"

      ```yaml
      sources:
        kas:
          branch: kirkstone-dev
          url: https://gitlab.com/soafee/ewaol/meta-ewaol-machine.git
          yaml: kas/ewaol/baremetal.yml:kas/machine/avadp.yml:kas/ewaol/ci-constraints.yml
      ```

    !!! note "kas_override.yml"

        ``` yaml
        header:
          version: 11

        repos:
          meta-ewaol:
            url: https://gitlab.com/soafee/ewaol/meta-ewaol.git
            refspec: refs/merge-requests/11/merge
            path: layers/meta-ewaol
        ```

      To submit a kas build with kas override file:

      ```shell
      tuxsuite bake submit kas.yaml -k kas_override.yml
      ```

!!! example "OE Build with manifest"

      ```yaml
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
        - licenses
      distro: rpb
      target: intltool-native
      machine: dragonboard-410c
      name: dragonboard-410c-rpb
      ```

    !!! info "manifest"

      ```xml
      <?xml version="1.0" encoding="UTF-8"?>
      <manifest>
      <extend-project name="ndechesne/meta-qcom" revision="2d91eb26e3cf0f6434f288518516750ac84329af"/>
      </manifest>
      ```

    To submit the build with manifest:

    ```shell
    tuxsuite bake submit build-definition.yaml --local-manifest local-manifest.xml
    ```

### Build definition format

The build definition can include the following fields:

* `sources` (dictionary with a single item): Should be one of **git_trees**, **repo**, **kas** or **android**.
* `git_trees` (list of dictionaries): Each dictionary will have **url**, **branch** and optionally **ref**.
* `repo` (a dictionary): Should have **branch**, **manifest** and **url**, describing where the manifests are hosted along with the branch and manifest file to be used in the build.
* `kas` (a dictionary): Each dictionary will have mandatory fields **url**, **yaml** and optional fields **branch**, **ref** and **sha**. No other fields are allowed when you use kas.
* `android` (a dictionary): Each dictionary will have **url**,
  **branch**, **manifest** with optional parameters such as
  **build_config**, **bazel**, **lunch_target** (userspace),
  **build_type** (userspace). No other fields are allowed when you use
  android.
* `distro`: The distro variable passed to OE build.
* `extraconfigs` (list of strings): Each entry corresponds to some extra configs that will be copied to conf folder and will be used while building the target. It is used only if build definition has sources as **repo** or **git_trees**.
* `envsetup`: Path to the script, relative to the source directory, that needs to be sourced to setup bitbake build environment.
* `machine`: The machine variable passed to OE build.
* `target`: Target passed to the bitbake command.
* `container`: The container used by Docker to do the build. We currently support **ubuntu-16.04**, **ubuntu-18.04**, **ubuntu-20.04**, **ubuntu-22.04**, **centos-8**, **debian-bullseye**, **debian-buster**, **debian-stretch**, **fedora-33**, **fedora-34**, **opensuse-leap-15.1**, **opensuse-leap-15.2**
* `local_conf` (list of strings): Each entry corresponds to a line in local.conf file. The list of string is converted to `local.conf` file.
* `bblayers_conf` (list of strings): Each entry corresponds to a line in bblayers.conf file. The list of string is converted to `bblayers.conf` file.
* `environment` (dictionary of environment variables): They are set before calling bitbake.
* `artifacts`: (list of strings): Artifacts or path of artifacts relative to `build` directory or `DEPLOY_DIR` to be published. If not specified then contents of `DEPLOY_DIR` will be published. Currently supported for builds which have sources as `repo`, `git_trees`,`kas` and `android` aosp builds.

### Examples

* [Layers with Repo](https://gitlab.com/Linaro/tuxsuite/-/blob/master/examples/bitbake/ledge-rpb.yaml)
* [Layers from git](https://gitlab.com/Linaro/tuxsuite/-/blob/master/examples/bitbake/lt-qcom.yaml)
* [YOCTO](https://gitlab.com/Linaro/tuxsuite/-/blob/master/examples/bitbake/yocto.yaml)
* [Kas](https://storage.tuxsuite.com/public/demo/demo/oebuilds/31UNTRXMK1wFaXHB5yFGa2c9trT/build-definition.yaml) and its [artifacts](https://storage.tuxsuite.com/public/demo/demo/oebuilds/31UNTRXMK1wFaXHB5yFGa2c9trT/)
