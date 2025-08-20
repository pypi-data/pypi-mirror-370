# OE Plan Specifications

## Version

Currently, tuxsuite only supports version 1.

```yaml
version: 1
```

## Name and description

The name and description are only used if they are not defined on the command line.

```yaml
name: plan name
description: plan description
```

They can be overridden on the command line:

```shell
tuxsuite plan --name "another name" --description "another description"
```

## Jobs

Most of the configuration takes place in the `jobs` section.

This section is a list of dictionary with one or two keys each.

Allowed combinations are:

* bake
* bakes
* bake and bakes

### Bake

A bake is defined by a dictionary:

```yaml
- bake:
    build definition
```

### Bakes

When specifying multiple oebuilds, the job should be a list of dictionaries like:

```yaml
- bakes:
  - build definition 1
  - build definition 2
  - build definition 3
  [....]
```

#### Build definitions

TuxOE uses build-definition to describe the build:

* the layers to download
* `local.conf` and `bblayers.conf` to use
* machine type
* distro targets
* ...

TuxOE can download the layers using either git protocol or the repo tool.

### Build definition format

=== "**Android Definition**"

    * container: Docker container to use for the build. Supported containers:
        - [x] ubuntu-16.04
        - [x] ubuntu-18.04
        - [x] ubuntu-20.04
        - [x] ubuntu-22.04
        - [x] centos-8
        - [x] debian-bullseye
        - [x] debian-buster
        - [x] debian-stretch
        - [x] fedora-33
        - [x] fedora-34
        - [x] opensuse-leap-15.1
        - [x] opensuse-leap-15.2
    * `name`: (optional) Any Name
    * `sources`:
        - `android`: Android repo source, branch, manifest, build-config and url.
    !!! Tip "Note"
        To build android 14.5.15 and common-android-mainline branch,
        field `bazel` should be passed in sources. It accepts boolean
        value and defaults to false.

    !!! Tip "Note"
        To build android userspace, field `lunch_target` should be
        passed in sources. It accepts the lunch target string. Also,
        the `build_type` should be passed which accepts values such as
        `user`, `userdebug` and `eng` as explained in
        <https://source.android.com/docs/setup/build/building>

=== "**Kas Definition**"

    * `container`: The container used by Docker to do the build. Supported containers are the same as the Android definition.
    * `artifacts`: (list of strings): Artifacts or path of artifacts relative to `build` directory or `DEPLOY_DIR` to be published. If not specified then contents of `DEPLOY_DIR` will be published.
    * `sources`:
        * `kas`: (a dictionary): Each dictionary should have **url**, **branch**, **yaml** and optionally **ref**.

=== "**OE Definition**"
    The build definition can include the following fields:

    * `sources`: (dictionary with a single item): Should be either one of **git_trees** or **repo**.
        * `git_trees`: (list of dictionaries): Each dictionary will have **url**, **branch** and optionally **ref**.
        *`repo`: (a dictionary): Should have **branch**, **manifest** and **url**, describing where the manifests are hosted along with the branch and manifest file to be used in the build.
    * `distro`: The distro variable passed to OE build.
    * `envsetup`: Path to the script, relative to the source directory, that needs to be sourced to setup bitbake build environment.
    * `extraconfigs` (list of strings): each entry corresponds to some extra configs that will be copied to conf folder and will be used while building the target. It is used only if build definition has sources as **repo** or **git_trees**.
    * `machine`: The machine variable passed to OE build.
    * `target`: Target passed to the bitbake command.
    * `container`: The container used by Docker to do the build. Supported containers are same as in android definition.
    * `local_conf`: (list of strings): Each entry corresponds to a line in local.conf file. The list of string is converted to `local.conf` file.
    * `bblayers_conf:` (list of strings): Each entry corresponds to a line in bblayers.conf file. The list of string is converted to `bblayers.conf` file.
    * `environment`: (dictionary of environment variables): They are set before calling bitbake.
    * `artifacts`: (list of strings): Artifacts or path of artifacts relative to `build` directory or `DEPLOY_DIR` to be published. If not specified then contents of `DEPLOY_DIR` will be published.

    !!! Note
        In OE build definition sources, either provide git_trees or repo, not both.

=== "**OpenBMC**"
    Build definition of OpenBMC is similar to OE Definition except for the following:

    - Distro is prefixed with `openbmc`.
    - sources should be `git_trees`.
