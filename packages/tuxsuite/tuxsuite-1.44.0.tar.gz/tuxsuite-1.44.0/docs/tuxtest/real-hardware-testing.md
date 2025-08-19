# Testing on Real hardware with TuxSuite

TuxSuite can now run user tests on Real Hardware using LAVA in the
backend. A build successfully completed in TuxBuild can be tested in a
real hardware in LAVA through TuxTest. This feature uses uses
[lava-test-plans](https://github.com/Linaro/lava-test-plans) in order
to submit a LAVA job to a LAVA instance.

**__NOTE__**: lava-test-plans [testcases](https://github.com/Linaro/lava-test-plans/tree/master/lava_test_plans/testcases) are accepted and not the
[testplans](https://github.com/Linaro/lava-test-plans/tree/master/lava_test_plans/testplans). The testcases found in
<https://github.com/Linaro/lava-test-plans/tree/master/lava_test_plans/testcases>
can be referred with its name.

**__NOTE__**: In order to get access to specific real hardware for
your group in TuxSuite, contact <tuxsuite@linaro.org>

## Options

There are two important options used when submitting a test using the
TuxSuite cli on real hardware.

### lab

The lab option is used to select the LAVA instance to which the test
should be submitted.

```shell
tuxsuite test --device x15 \
    --lab https://lkft.validation.linaro.org \
    --kernel https://storage.tuxsuite.com/public/linaro/lkft/builds/2SzdP2Y00UvIcS3f56EaTILWuLX/zImage \
    --modules https://storage.tuxsuite.com/public/linaro/lkft/builds/2SzdP2Y00UvIcS3f56EaTILWuLX/modules.tar.xz \
    --rootfs https://storage.tuxboot.com/debian/20230714/bookworm/armhf/rootfs.ext4.xz \
    --dtb https://storage.tuxsuite.com/public/linaro/lkft/builds/2SzdP2Y00UvIcS3f56EaTILWuLX/dtbs/am57xx-beagle-x15.dtb \
    --parameters DEPLOY_OS=debian
```

This value can also be set in the tuxsuite config file
`~/.config/tuxsuite/config.ini` as follows:

`lab = https://lkft.validation.linaro.org`

It can also be supplied as an environment variable which is shown as
follows:

`export TUXSUITE_LAB=https://lkft.validation.linaro.org`

**__NOTE__**: The default LAVA lab instance is
<https://lkft.validation.linaro.org>

### lava-test-plans-project

The lava-test-plans-project option is used to choose the
lava-test-plans project.

```shell
tuxsuite test --device x15 \
    --lava-test-plans-project lkft \
    --kernel https://storage.tuxsuite.com/public/linaro/lkft/builds/2SzdP2Y00UvIcS3f56EaTILWuLX/zImage \
    --modules https://storage.tuxsuite.com/public/linaro/lkft/builds/2SzdP2Y00UvIcS3f56EaTILWuLX/modules.tar.xz \
    --rootfs https://storage.tuxboot.com/debian/20230714/bookworm/armhf/rootfs.ext4.xz \
    --dtb https://storage.tuxsuite.com/public/linaro/lkft/builds/2SzdP2Y00UvIcS3f56EaTILWuLX/dtbs/am57xx-beagle-x15.dtb \
    --parameters DEPLOY_OS=debian
```

This value can also be set in the tuxsuite config file
`~/.config/tuxsuite/config.ini` as follows:

`lava_test_plans_project = lkft`

It can also be supplied as an environment variable which is shown as
follows:

`export TUXSUITE_LAVA_TEST_PLANS_PROJECT=lkft`

**__NOTE__**: The default lava-test-plans-project is `None`

## Plan with build and boot test

!!! info "A sample plan"
    <details>
    <summary>Click to see the plan contents</summary>

    ```
    lkftfragments: &lkftfragments
      - &frag-lkft-base https://raw.githubusercontent.com/Linaro/meta-lkft/kirkstone/meta/recipes-kernel/linux/files/lkft.config
      - &frag-lkft-crypto https://raw.githubusercontent.com/Linaro/meta-lkft/kirkstone/meta/recipes-kernel/linux/files/lkft-crypto.config
      - &frag-lkft-distro https://raw.githubusercontent.com/Linaro/meta-lkft/kirkstone/meta/recipes-kernel/linux/files/distro-overrides.config
      - &frag-lkft-systemd https://raw.githubusercontent.com/Linaro/meta-lkft/kirkstone/meta/recipes-kernel/linux/files/systemd.config
      - &frag-lkft-virtio https://raw.githubusercontent.com/Linaro/meta-lkft/kirkstone/meta/recipes-kernel/linux/files/virtio.config

    version: 1
    name: x15 build and boot test.
    description: Demonstrate a build and boot test with x15 via real hardware
    jobs:
    - name: arm-lkftconfig-dut
      builds:
        - build_name: gcc-10-lkftconfig
          target_arch: arm
          toolchain: gcc-10
          kconfig: [ defconfig, *frag-lkft-base, *frag-lkft-crypto, *frag-lkft-distro, *frag-lkft-systemd, *frag-lkft-virtio, CONFIG_ARM_TI_CPUFREQ=y, CONFIG_SERIAL_8250_OMAP=y, CONFIG_POSIX_MQUEUE=y, CONFIG_OF=y, CONFIG_SYN_COOKIES=y, CONFIG_SCHEDSTATS=y, CONFIG_AHCI_DWC=y, CONFIG_KFENCE=n ]
      tests:
        - device: x15
          boot_args: rw
          parameters: {DEPLOY_OS: "debian"}
          dtb: am57xx-beagle-x15.dtb
          rootfs: https://storage.tuxboot.com/debian/20230714/bookworm/armhf/rootfs.ext4.xz
    ```

    </details>

Submitting the above plan file will build the kernel and submit the
test as a LAVA job with the kernel build artifacts.

```shell
tuxsuite plan submit \
    --git-repo https://gitlab.com/Linaro/lkft/mirrors/torvalds/linux-mainline \
    --git-ref master \
    --lab https://validation.linaro.org/ \
    --lava-test-plans-project lkft \
    x15-boot-plan.yaml
```

## Additional parameters to lava-test-plans

Any extra parameters to lava-test-plans can be supplied with the
`--parameters` option in the command line. The `--parameters` option
can be repeated multiple times. This can also be used within a plan as
a parameters dictionary.

```shell
tuxsuite test --device x15 \
    --lab https://lkft.validation.linaro.org \
    --kernel https://storage.tuxsuite.com/public/linaro/lkft/builds/2SzdP2Y00UvIcS3f56EaTILWuLX/zImage \
    --modules https://storage.tuxsuite.com/public/linaro/lkft/builds/2SzdP2Y00UvIcS3f56EaTILWuLX/modules.tar.xz \
    --rootfs https://storage.tuxboot.com/debian/20230714/bookworm/armhf/rootfs.ext4.xz \
    --dtb https://storage.tuxsuite.com/public/linaro/lkft/builds/2SzdP2Y00UvIcS3f56EaTILWuLX/dtbs/am57xx-beagle-x15.dtb \
    --parameters DEPLOY_OS=debian \
    --parameters KVM_UNIT_TESTS_REVISION=ca85dda2671e88d34acfbca6de48a9ab32b1810d \
    --parameters LAVA_JOB_PRIORITY=5
```

!!! info "Plan with multiple parameters"
    <details>
    <summary>Click to see the plan contents</summary>

    ```
    lkftfragments: &lkftfragments
      - &frag-lkft-base https://raw.githubusercontent.com/Linaro/meta-lkft/kirkstone/meta/recipes-kernel/linux/files/lkft.config
      - &frag-lkft-crypto https://raw.githubusercontent.com/Linaro/meta-lkft/kirkstone/meta/recipes-kernel/linux/files/lkft-crypto.config
      - &frag-lkft-distro https://raw.githubusercontent.com/Linaro/meta-lkft/kirkstone/meta/recipes-kernel/linux/files/distro-overrides.config
      - &frag-lkft-systemd https://raw.githubusercontent.com/Linaro/meta-lkft/kirkstone/meta/recipes-kernel/linux/files/systemd.config
      - &frag-lkft-virtio https://raw.githubusercontent.com/Linaro/meta-lkft/kirkstone/meta/recipes-kernel/linux/files/virtio.config

    version: 1
    name: x15 build and boot test.
    description: Demonstrate a build and boot test with x15 via real hardware
    jobs:
    - name: arm-lkftconfig-dut
      builds:
        - build_name: gcc-10-lkftconfig
          target_arch: arm
          toolchain: gcc-10
          kconfig: [ defconfig, *frag-lkft-base, *frag-lkft-crypto, *frag-lkft-distro, *frag-lkft-systemd, *frag-lkft-virtio, CONFIG_ARM_TI_CPUFREQ=y, CONFIG_SERIAL_8250_OMAP=y, CONFIG_POSIX_MQUEUE=y, CONFIG_OF=y, CONFIG_SYN_COOKIES=y, CONFIG_SCHEDSTATS=y, CONFIG_AHCI_DWC=y, CONFIG_KFENCE=n ]
      tests:
        - device: x15
          boot_args: rw
          parameters: {DEPLOY_OS: "debian", OVERLAY_PATH: "/", KVM_UNIT_TESTS_REVISION: "ca85dda2671e88d34acfbca6de48a9ab32b1810d", LAVA_JOB_PRIORITY: "5"}
          dtb: am57xx-beagle-x15.dtb
          rootfs: https://storage.tuxboot.com/debian/20230714/bookworm/armhf/rootfs.ext4.xz
    ```

    </details>

Some commonly used parameters are listed below, which is not
exhaustive though:

- DEPLOY_OS
- LAVA_JOB_PRIORITY *(The default is 10)*
- OVERLAY_PATH
- KSELFTEST_PATH
- KVM_UNIT_TESTS_REVISION
- TAGS
- PROJECT_NAME
- TEST_DEFINITIONS_REPOSITORY
- TDEFINITIONS_REVISION

!!! info "Examples"
    Many example plans for different real hardwares can be found in <https://gitlab.com/Linaro/tuxsuite/-/tree/master/examples/test-on-real-hardware>

## Supported real hardwares

- bcm2711-rpi-4-b
- dragonboard-410c
- dragonboard-845c
- e850-96
- hi6220-hikey-r2
- i386
- juno-r2
- qrb5165-rb5
- rk3399-rock-pi-4b
- x15
- x86
