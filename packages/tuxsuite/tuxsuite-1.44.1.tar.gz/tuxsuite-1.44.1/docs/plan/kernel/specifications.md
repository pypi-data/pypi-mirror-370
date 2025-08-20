# Plan Specifications

A plan is a yaml file with the following specification.

## Full plan example

Full plan example:

```yaml
version: 1
name: <plan name>
description: <plan description>
jobs:
- build: {toolchain: gcc-8, target_arch: i386, kconfig: tinyconfig}
  sanity_test: {device: qemu-i386}
  test: {device: qemu-i386, tests: [ltp-smoke]}

- builds:
  - {toolchain: gcc-8, target_arch: i386, kconfig: tinyconfig}
  - {toolchain: gcc-9, target_arch: i386, kconfig: tinyconfig}
  - {toolchain: gcc-10, target_arch: i386, kconfig: tinyconfig}
  test: {device: qemu-i386, tests: [ltp-smoke]}
- builds:
  - {toolchain: clang-10, target_arch: i386, kconfig: tinyconfig}
  - {toolchain: clang-11, target_arch: i386, kconfig: tinyconfig}
  - {toolchain: clang-nightly, target_arch: i386, kconfig: tinyconfig}
  test: {device: qemu-i386}

- build: {toolchain: clang-nightly, target_arch: i386, kconfig: tinyconfig}
  tests:
  - {device: qemu-i386}
  - {device: qemu-i386, tests: [ltp-smoke]}

- builds:
  - {toolchain: gcc-8, target_arch: i386, kconfig: tinyconfig}
  - {toolchain: gcc-9, target_arch: i386, kconfig: tinyconfig}
  - {toolchain: gcc-10, target_arch: i386, kconfig: tinyconfig}
  tests:
  - {device: qemu-i386}
  - {device: qemu-i386, tests: [ltp-smoke]}

- tests:
  - {kernel: https://storage.tuxboot.com/arm64/Image, device: qemu-arm64, tests: [ltp-smoke]}
  - {kernel: https://storage.tuxboot.com/i386/bzImage, device: qemu-i386, tests: [ltp-smoke]}
  - {kernel: https://storage.tuxboot.com/mips64/vmlinux, device: qemu-mips64, tests: [ltp-smoke]}
  - {kernel: https://storage.tuxboot.com/ppc64/vmlinux, device: qemu-ppc64, tests: [ltp-smoke]}
  - {kernel: https://storage.tuxboot.com/riscv64/Image, device: qemu-riscv64, tests: [ltp-smoke]}
  - {kernel: https://storage.tuxboot.com/x86_64/bzImage, device: qemu-x86_64, tests: [ltp-smoke]}
```

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

```
tuxsuite plan --name "another name" --description "another description"
```

## Jobs

Most of the configuration takes place in the `jobs` section.

This section is a list of dictionary with one or two keys each.

Allowed combinations are:

* builds
* builds and test
* builds and tests
* build and test
* build and tests
* tests

### Combinations

Each combinations has a different meaning:

* **builds**: list of builds
* **builds** and **test**: list of builds. For each build, the given test will be run
* **builds** and **tests**: list of builds. For each build, the given tests will be run
* **build** and **test**: a single build. The test will be run for this build
* **build** and **tests**: a single build. Every test will be run for this build
* **tests**: a list of kernels and modules to test
* **build**, **sanity_test** and **test**: A single build. Run the given sanity_test for that build. If the sanity_test passes, then the given test will be run for that build.
* **build**, **sanity_test** and **tests**: A single build. Run the given sanity_test for that build. If the sanity_test passes, then the given list of tests will be run for that build.
* **builds**, **sanity_test** and **test**: list of builds. For each build, run the given sanity_test. For each build if the sanity_test passes, then the given test will be run for that build.
* **builds**, **sanity_test** and **tests**: list of builds. For each build, run the given sanity_test. For each build if the sanity_test passes, then the given list of tests will be run for that build.

### Builds

A build is defined by a dictionary:

```yaml
toolchain: gcc-8
target_arch: i386
kconfig: defconfig
```

When specifying multiple builds, the job should be a list of dictionaries like:

```yaml
- builds:
  - {toolchain: gcc-8, target_arch: i386, kconfig: tinyconfig}
  - {toolchain: gcc-9, target_arch: i386, kconfig: tinyconfig}
  - {toolchain: gcc-10, target_arch: i386, kconfig: tinyconfig}
```

### Tests

A test is defined by a dictionary:

```yaml
device: qemu-i386
tests: [ltp-smoke]
```

In this case, the test is valid only when linked with a test.

To define a single test, a `kernel` is mandatory:

```yaml
device: qemu-i386
tests: [ltp-smoke]
kernel: https://storage.tuxboot.com/i386/bzImage
```

For ltp test suites, you can use sharding by specifying the sharding level:

```yaml
- builds:
  - {toolchain: gcc-8, target_arch: i386, kconfig: tinyconfig}
  tests:
  - {device: qemu-i386, tests: [ltp-syscalls], sharding: 10}
```

This will create 10 tests with parameters to only run one tenth of test tests.
