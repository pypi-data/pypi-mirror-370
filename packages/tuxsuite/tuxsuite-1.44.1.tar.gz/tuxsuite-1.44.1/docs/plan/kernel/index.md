# TuxSuite Plan

A tuxsuite plan is a combination of builds and tests.

For each build, it's possible (but optional) to define tests that would be
launched when the build is successful. This dependency is declared at
submission time and later handled directly by the server.

A plan could be made of:

* stand alone builds
* stand alone tests
* builds then trigger tests
* builds followed by a quick sanity-test and then trigger tests

## Example

This plan will build the given linux kernel tree with every available
toolchain on `arm64`, `i386` and `x86_64`.

```yaml
version: 1
name: kernel build
description: Build linux kernel with every toolchain
jobs:
- builds:
  - {toolchain: gcc-8, target_arch: arm64, kconfig: defconfig}
  - {toolchain: gcc-9, target_arch: arm64, kconfig: defconfig}
  - {toolchain: gcc-10, target_arch: arm64, kconfig: defconfig}
  - {toolchain: clang-10, target_arch: arm64, kconfig: defconfig}
  - {toolchain: clang-11, target_arch: arm64, kconfig: defconfig}
  - {toolchain: clang-12, target_arch: arm64, kconfig: defconfig}
  - {toolchain: clang-nightly, target_arch: arm64, kconfig: defconfig}
  - {toolchain: gcc-8, target_arch: i386, kconfig: defconfig}
  - {toolchain: gcc-9, target_arch: i386, kconfig: defconfig}
  - {toolchain: gcc-10, target_arch: i386, kconfig: defconfig}
  - {toolchain: clang-10, target_arch: i386, kconfig: defconfig}
  - {toolchain: clang-11, target_arch: i386, kconfig: defconfig}
  - {toolchain: clang-12, target_arch: i386, kconfig: defconfig}
  - {toolchain: clang-nightly, target_arch: i386, kconfig: defconfig}
  - {toolchain: gcc-8, target_arch: x86_64, kconfig: defconfig}
  - {toolchain: gcc-9, target_arch: x86_64, kconfig: defconfig}
  - {toolchain: gcc-10, target_arch: x86_64, kconfig: defconfig}
  - {toolchain: clang-10, target_arch: x86_64, kconfig: defconfig}
  - {toolchain: clang-11, target_arch: x86_64, kconfig: defconfig}
  - {toolchain: clang-12, target_arch: x86_64, kconfig: defconfig}
  - {toolchain: clang-nightly, target_arch: x86_64, kconfig: defconfig}
```

You can validate Linus Torvald's tree with:

```shell
tuxsuite plan \
    --git-repo https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git \
    --git-ref master --no-wait \
    plan.yaml
```

`--no-wait` is an optional argument which submits the plan and returns
immediately printing the plan artifacts to `stdout`.

## Private plan

A plan is private if authentication is required to access the artifacts.
To make a plan private `-P/--private` option should be passed as optional argument while submitting a plan.

`Note`: A private plan submitted along with builds and tests, would lead to failure of tests as currently we don't support accessing build data for dependent tests from private build storage. However, builds will pass.
