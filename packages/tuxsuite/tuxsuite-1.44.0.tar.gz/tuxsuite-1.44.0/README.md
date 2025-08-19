<div align="center">
  <img src="https://gitlab.com/Linaro/tuxsuite/raw/master/tuxsuite_logo.png" alt="TuxSuite Logo" width="50%" />
</div>

[![Pipeline Status](https://gitlab.com/Linaro/tuxsuite/badges/master/pipeline.svg)](https://gitlab.com/Linaro/tuxsuite/pipelines)
[![coverage report](https://gitlab.com/Linaro/tuxsuite/badges/master/coverage.svg)](https://gitlab.com/Linaro/tuxsuite/commits/master)
[![PyPI version](https://badge.fury.io/py/tuxsuite.svg)](https://pypi.org/project/tuxsuite/)
[![Docker Pulls](https://img.shields.io/docker/pulls/tuxsuite/tuxsuite.svg)](https://hub.docker.com/r/tuxsuite/tuxsuite)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI - License](https://img.shields.io/pypi/l/tuxsuite)](https://gitlab.com/Linaro/tuxsuite/blob/master/LICENSE)

[Documentation](https://docs.tuxsuite.com/) - [Repository](https://gitlab.com/Linaro/tuxsuite) - [Issues](https://gitlab.com/Linaro/tuxsuite/-/issues)

[TuxSuite](https://tuxsuite.com), by Linaro, is a suite of tools and services
to help with Linux kernel development. The TuxSuite CLI (this repo) is the
supported interface to TuxBuild, TuxTest and TuxOE.

To request access, email us at tuxsuite@linaro.org or fill out our [access
request form](https://forms.gle/3NaW5fuNykGstsMq6).

[[_TOC_]]

# Introduction

The TuxSuite CLI supports three services: TuxBuild, TuxTest and TuxOE.

## TuxBuild

<img src="docs/images/tuxbuild_icon.svg" alt="TuxBuild Logo" width="100px" align="left">

TuxBuild is an on demand API for building massive quantities of Linux kernels
in parallel. It is used at scale in production by
[LKFT](https://lkft.linaro.org/) and
[ClangBuiltLinux](https://clangbuiltlinux.github.io/) as well as many
individual Linux kernel engineers.

TuxBuild is accessed by running `tuxsuite build` and `tuxsuite plan`.

## TuxTest

<img src="docs/images/tuxtest_icon.svg" alt="TuxTest Logo" width="100px" align="left">

TuxTest is an on demand API for testing Linux kernels reliably and quickly. It
is currently in Beta phase and is already available to TuxBuild users.

## TuxOE

<img src="docs/images/tuxoe_icon.svg" alt="TuxOE Logo" width="100px" align="left">

TuxOE is an on demand API for building Yocto/OpenEmbedded in parallel at scale.
It is used at scale in production by
[LKFT](https://lkft.linaro.org/)

## Install and Configure

### Install using pip

TuxSuite requires Python version 3.6 or greater, and is available using pip.

To install tuxsuite on your system globally:

```
sudo pip3 install -U tuxsuite
```

To install tuxsuite to your home directory at ~/.local/bin:

```
pip3 install -U --user tuxsuite
```

To upgrade tuxsuite to the latest version, run the same command you ran to
install it.

### Install using Debian packages

TuxSuite provides Debian packages that have minimal dependencies, and
should work on any Debian or Debian-based (Ubuntu, etc) system.

1) Download the repository signing key and save it to
/etc/apt/trusted.gpg.d/tuxsuite.gpg.

```
# wget -O /etc/apt/trusted.gpg.d/tuxsuite.gpg https://repo.tuxsuite.com/packages/signing-key.gpg
```

2) Create /etc/apt/sources.list.d/tuxsuite.list with the following contents:

```
deb https://repo.tuxsuite.com/packages/ ./
```

3) Install tuxsuite as you would any other package:

```
apt update
apt install tuxsuite
```

Upgrading tuxsuite will work just like it would for any other package
(apt update, apt upgrade).

### Install using RPM packages

TuxSuite provides RPM packages that have minimal dependencies, and
should work on any RPM-based (Fedora, etc) system.

1) Create /etc/yum.repos.d/tuxsuite.repo with the following contents:

```
[tuxsuite]
name=tuxsuite
type=rpm-md
baseurl=https://repo.tuxsuite.com/packages/
gpgcheck=1
gpgkey=https://repo.tuxsuite.com/packages/repodata/repomd.xml.key
enabled=1
```

2) Install tuxsuite as you would any other package:

```
dnf install tuxsuite
```

Upgrades will be available in the same repository, so you can get them
using the same procedure you already use to get other updates for your
system.

### Install using docker

tuxsuite is also available as a docker container at
[tuxsuite/tuxsuite](https://hub.docker.com/r/tuxsuite/tuxsuite).

For example, to run tuxsuite via docker:

```
docker run tuxsuite/tuxsuite tuxsuite build --help
```

### Install using docker from tuxsuite public ECR

tuxsuite is also available as a docker container at
[gallery.ecr.aws/tuxsuite/tuxsuite](https://gallery.ecr.aws/tuxsuite/tuxsuite).

For example, to run tuxsuite via docker obtained from tuxsuite's
public ECR:

```
docker run public.ecr.aws/tuxsuite/tuxsuite:latest tuxsuite build --help
```

### Running uninstalled

If you don't want to or can't install TuxSuite, you can run it directly from the
source directory. After getting the sources via git or something else, there is
a `run` script that will do the right thing for you: you can either use that
script directly, or symlink it to a directory in your `PATH`.

```shell
/path/to/tuxsuite/run --help
sudo ln -s /path/to/tuxsuite/run /usr/local/bin/tuxsuite && tuxsuite --help
```

### Setup Config

The Authentication token needs to be stored in `~/.config/tuxsuite/config.ini`.
The minimal format of the ini file is given below:

```
$ cat ~/.config/tuxsuite/config.ini
[default]
token=vXXXXXXXYYYYYYYYYZZZZZZZZZZZZZZZZZZZg
```

Alternatively, the `TUXSUITE_TOKEN` environment variable may be provided.

If you do not have a tuxsuite token, please reach out to us at
tuxsuite@linaro.org.

## Examples

### tuxsuite build

Submit a build request using the tuxsuite command line interface. This will
wait for the build to complete before returning by default.

```
tuxsuite build --git-repo 'https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git' --git-ref master --target-arch arm64 --kconfig defconfig --toolchain gcc-9
```

### tuxsuite plan

Submit a plan request using the tuxsuite command line interface. The plan file
describes the list of builds along with the tests to run for each successful
build. When one build is finished, the corresponding test is automatically
started.

Create a plan configuration file:

```yaml
version: 1
name: kernel validation
description: Build and test linux kernel with every toolchains
jobs:
- builds:
  - {toolchain: gcc-8, target_arch: arm64, kconfig: defconfig}
  - {toolchain: gcc-9, target_arch: arm64, kconfig: defconfig}
  - {toolchain: gcc-10, target_arch: arm64, kconfig: defconfig}
  - {toolchain: gcc-11, target_arch: arm64, kconfig: defconfig}
  - {toolchain: gcc-12, target_arch: arm64, kconfig: defconfig}
  - {toolchain: clang-10, target_arch: arm64, kconfig: defconfig}
  - {toolchain: clang-11, target_arch: arm64, kconfig: defconfig}
  - {toolchain: clang-12, target_arch: arm64, kconfig: defconfig}
  - {toolchain: clang-13, target_arch: arm64, kconfig: defconfig}
  - {toolchain: clang-14, target_arch: arm64, kconfig: defconfig}
  - {toolchain: clang-15, target_arch: arm64, kconfig: defconfig}
  - {toolchain: clang-16, target_arch: arm64, kconfig: defconfig}
  - {toolchain: clang-nightly, target_arch: arm64, kconfig: defconfig}
  test: {device: qemu-arm64, tests: [ltp-smoke]}
- builds:
  - {toolchain: gcc-8, target_arch: i386, kconfig: defconfig}
  - {toolchain: gcc-9, target_arch: i386, kconfig: defconfig}
  - {toolchain: gcc-10, target_arch: i386, kconfig: defconfig}
  - {toolchain: gcc-11, target_arch: i386, kconfig: defconfig}
  - {toolchain: gcc-12, target_arch: i386, kconfig: defconfig}
  - {toolchain: clang-10, target_arch: i386, kconfig: defconfig}
  - {toolchain: clang-11, target_arch: i386, kconfig: defconfig}
  - {toolchain: clang-12, target_arch: i386, kconfig: defconfig}
  - {toolchain: clang-13, target_arch: i386, kconfig: defconfig}
  - {toolchain: clang-14, target_arch: i386, kconfig: defconfig}
  - {toolchain: clang-15, target_arch: i386, kconfig: defconfig}
  - {toolchain: clang-16, target_arch: i386, kconfig: defconfig}
  - {toolchain: clang-nightly, target_arch: i386, kconfig: defconfig}
  test: {device: qemu-i386, tests: [ltp-smoke]}
- builds:
  - {toolchain: gcc-8, target_arch: x86_64, kconfig: defconfig}
  - {toolchain: gcc-9, target_arch: x86_64, kconfig: defconfig}
  - {toolchain: gcc-10, target_arch: x86_64, kconfig: defconfig}
  - {toolchain: gcc-11, target_arch: x86_64, kconfig: defconfig}
  - {toolchain: gcc-12, target_arch: x86_64, kconfig: defconfig}
  - {toolchain: clang-10, target_arch: x86_64, kconfig: defconfig}
  - {toolchain: clang-11, target_arch: x86_64, kconfig: defconfig}
  - {toolchain: clang-12, target_arch: x86_64, kconfig: defconfig}
  - {toolchain: clang-13, target_arch: x86_64, kconfig: defconfig}
  - {toolchain: clang-14, target_arch: x86_64, kconfig: defconfig}
  - {toolchain: clang-15, target_arch: x86_64, kconfig: defconfig}
  - {toolchain: clang-16, target_arch: x86_64, kconfig: defconfig}
  - {toolchain: clang-nightly, target_arch: x86_64, kconfig: defconfig}
  test: {device: qemu-x86_64, tests: [ltp-smoke]}
```

Submit the plan with:

```
tuxsuite plan --git-repo https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git --git-ref master plan.yaml
```

### tuxsuite test

Submit a test request using the tuxsuite command line interface. This will wait
for the test to complete before returning.

```
tuxsuite test --device qemu-x86_64 --kernel https://storage.tuxboot.com/x86_64/bzImage --tests ltp-smoke
```

### tuxsuite bake

Submit an OE build request using the tuxsuite command line interface. This will wait
for the OE build to complete before returning.

```
tuxsuite bake submit build-definition.yaml
```

Sample build definition file for OE bake build.

```yaml
container: ubuntu-20.04
distro: oniro-linux
environment:
  TEMPLATECONF: ../oniro/flavours/linux
envsetup: oe-core/oe-init-build-env
machine: qemux86-64
sources:
  repo:
    branch: kirkstone
    manifest: default.xml
    url: https://gitlab.eclipse.org/eclipse/oniro-core/oniro
target: intltool-native
```

### tuxsuite results

The `results` sub-command provide a way to get the status of a
build/test/plan that has been previously submitted.

The `results` sub-command when invoked with `fetch` sub-command shows the
latest builds, tests, and plans that have been previously submitted by
the user.

```shell
tuxsuite results fetch
```

The `build` option fetches the `results` of the `build` based on the
given `uid`

```shell
tuxsuite results --build 1t26TJROt6zoxIw3YS2OlMXMGzK
```

The `test` option fetches the `results` of the `test` based on the
given `uid`

```shell
tuxsuite results --test 1s20dnMkE94e3BHW8pEbOWuyL6z
```

The `plan` option fetches the `results` of the `plan` based on the
given `uid`

```shell
tuxsuite results --plan 1t2UxTeU15WDwvhloPFUqjmr3CX
```

## Projects and Developers using tuxsuite

- [LKFT](https://lkft.linaro.org/) - Linaro's Linux Kernel Functional Testing
  uses tuxsuite with
  [gitlab-ci](https://about.gitlab.com/stages-devops-lifecycle/continuous-integration/)
  to continuously build upstream Linux kernels. The kernels are then
  functionally tested on a variety of hardware using
  [LAVA](https://www.lavasoftware.org/).
- [ClangBuiltLinux](https://clangbuiltlinux.github.io/) uses TuxBuild to
  validate hundreds of combinations of Linux kernels and LLVM environments.
- Lee Jones uses a [GitLab CI
  pipeline](https://gitlab.com/Linaro/lkft/users/lee.jones/lag-linaro-linux/-/pipelines)
  to validate his 3.18 kernel maintainership. The gitlab pipeline, tuxsuite
  config, and README.md documenting its setup are defined in the
  [kernel-pipeline](https://gitlab.com/Linaro/lkft/users/lee.jones/kernel-pipeline)
  repository.

## Community and Support

The TuxSuite team may be engaged through chat, email, or gitlab issues.

To chat with us, [join our public Discord](https://discord.gg/4hhTzUrj5M), or
our IRC channels #tuxsuite and #tuxmake on
[Libera Chat](https://libera.chat/).

Questions, comments or feedback are always welcome by private email at
tuxsuite@linaro.org.

Finally, gitlab issues are used to track bugs and feature requests in both
[tuxsuite](https://gitlab.com/Linaro/tuxsuite/-/issues) and
[tuxmake](https://gitlab.com/Linaro/tuxmake/-/issues) projects.
