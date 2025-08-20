# Examples

## Kernel builds

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
    --git-ref master \
    plan.yaml
```

## Kernel testing

This plan will test a given set of kernels that are already built.

```yaml
version: 1
name: kernel test
description: Test linux kernels
jobs:
- tests:
    - {kernel: https://storage.tuxboot.com/arm64/Image, device: qemu-arm64, tests: [ltp-smoke]}
    - {kernel: https://storage.tuxboot.com/i386/bzImage, device: qemu-i386, tests: [ltp-smoke]}
    - {kernel: https://storage.tuxboot.com/mips64/vmlinux, device: qemu-mips64, tests: [ltp-smoke]}
    - {kernel: https://storage.tuxboot.com/ppc64/vmlinux, device: qemu-ppc64, tests: [ltp-smoke]}
    - {kernel: https://storage.tuxboot.com/riscv64/Image, device: qemu-riscv64, tests: [ltp-smoke]}
    - {kernel: https://storage.tuxboot.com/x86_64/bzImage, device: qemu-x86_64, tests: [ltp-smoke]}
```

You can validate these kernels with:

```shell
tuxsuite plan plan.yaml
```

## Full kernel validation

This plan will build and test the given linux tree with every available
toolchain and architecture.

```yaml
version: 1
name: full kernel validation
description: Build and test linux kernel with every toolchain
jobs:
- name: armv5
  builds:
    - {toolchain: gcc-8, target_arch: arm, kconfig: [versatile_defconfig, "CONFIG_PCI=y", "CONFIG_PCI_VERSATILE=y", "CONFIG_SCSI=y", "CONFIG_BLK_DEV_SD=y", "CONFIG_SCSI_SYM53C8XX_2=y", "CONFIG_EXT4_FS=y"]}
    - {toolchain: gcc-9, target_arch: arm, kconfig: [versatile_defconfig, "CONFIG_PCI=y", "CONFIG_PCI_VERSATILE=y", "CONFIG_SCSI=y", "CONFIG_BLK_DEV_SD=y", "CONFIG_SCSI_SYM53C8XX_2=y", "CONFIG_EXT4_FS=y"]}
    - {toolchain: gcc-10, target_arch: arm, kconfig: [versatile_defconfig, "CONFIG_PCI=y", "CONFIG_PCI_VERSATILE=y", "CONFIG_SCSI=y", "CONFIG_BLK_DEV_SD=y", "CONFIG_SCSI_SYM53C8XX_2=y", "CONFIG_EXT4_FS=y"]}
    - {toolchain: gcc-11, target_arch: arm, kconfig: [versatile_defconfig, "CONFIG_PCI=y", "CONFIG_PCI_VERSATILE=y", "CONFIG_SCSI=y", "CONFIG_BLK_DEV_SD=y", "CONFIG_SCSI_SYM53C8XX_2=y", "CONFIG_EXT4_FS=y"]}
    - {toolchain: clang-10, target_arch: arm, kconfig: [versatile_defconfig, "CONFIG_PCI=y", "CONFIG_PCI_VERSATILE=y", "CONFIG_SCSI=y", "CONFIG_BLK_DEV_SD=y", "CONFIG_SCSI_SYM53C8XX_2=y", "CONFIG_EXT4_FS=y"]}
    - {toolchain: clang-11, target_arch: arm, kconfig: [versatile_defconfig, "CONFIG_PCI=y", "CONFIG_PCI_VERSATILE=y", "CONFIG_SCSI=y", "CONFIG_BLK_DEV_SD=y", "CONFIG_SCSI_SYM53C8XX_2=y", "CONFIG_EXT4_FS=y"]}
    - {toolchain: clang-12, target_arch: arm, kconfig: [versatile_defconfig, "CONFIG_PCI=y", "CONFIG_PCI_VERSATILE=y", "CONFIG_SCSI=y", "CONFIG_BLK_DEV_SD=y", "CONFIG_SCSI_SYM53C8XX_2=y", "CONFIG_EXT4_FS=y"]}
    - {toolchain: clang-nightly, target_arch: arm, kconfig: [versatile_defconfig, "CONFIG_PCI=y", "CONFIG_PCI_VERSATILE=y", "CONFIG_SCSI=y", "CONFIG_BLK_DEV_SD=y", "CONFIG_SCSI_SYM53C8XX_2=y", "CONFIG_EXT4_FS=y"]}
  test: {device: qemu-armv5, tests: [ltp-smoke]}
- name: armv7
  builds:
    - {toolchain: gcc-8, target_arch: arm, kconfig: multi_v7_defconfig}
    - {toolchain: gcc-9, target_arch: arm, kconfig: multi_v7_defconfig}
    - {toolchain: gcc-10, target_arch: arm, kconfig: multi_v7_defconfig}
    - {toolchain: gcc-11, target_arch: arm, kconfig: multi_v7_defconfig}
    - {toolchain: clang-10, target_arch: arm, kconfig: multi_v7_defconfig}
    - {toolchain: clang-11, target_arch: arm, kconfig: multi_v7_defconfig}
    - {toolchain: clang-12, target_arch: arm, kconfig: multi_v7_defconfig}
    - {toolchain: clang-nightly, target_arch: arm, kconfig: multi_v7_defconfig}
  test: {device: qemu-armv7, tests: [ltp-smoke]}
- name: arm64
  builds:
    - {toolchain: gcc-8, target_arch: arm64, kconfig: defconfig}
    - {toolchain: gcc-9, target_arch: arm64, kconfig: defconfig}
    - {toolchain: gcc-10, target_arch: arm64, kconfig: defconfig}
    - {toolchain: gcc-11, target_arch: arm64, kconfig: defconfig}
    - {toolchain: clang-10, target_arch: arm64, kconfig: defconfig}
    - {toolchain: clang-11, target_arch: arm64, kconfig: defconfig}
    - {toolchain: clang-12, target_arch: arm64, kconfig: defconfig}
    - {toolchain: clang-nightly, target_arch: arm64, kconfig: defconfig}
  test: {device: qemu-arm64, tests: [ltp-smoke]}
- name: i386
  builds:
    - {toolchain: gcc-8, target_arch: i386, kconfig: defconfig}
    - {toolchain: gcc-9, target_arch: i386, kconfig: defconfig}
    - {toolchain: gcc-10, target_arch: i386, kconfig: defconfig}
    - {toolchain: gcc-11, target_arch: i386, kconfig: defconfig}
    - {toolchain: clang-10, target_arch: i386, kconfig: defconfig}
    - {toolchain: clang-11, target_arch: i386, kconfig: defconfig}
    - {toolchain: clang-12, target_arch: i386, kconfig: defconfig}
    - {toolchain: clang-nightly, target_arch: i386, kconfig: defconfig}
  test: {device: qemu-i386, tests: [ltp-smoke]}
- name: mips64
  builds:
    - {toolchain: gcc-8, target_arch: mips, kernel_image: vmlinux, kconfig: [malta_defconfig, "https://storage.tuxboot.com/mips64/malta_defconfig"]}
    - {toolchain: gcc-9, target_arch: mips, kernel_image: vmlinux, kconfig: [malta_defconfig, "https://storage.tuxboot.com/mips64/malta_defconfig"]}
    - {toolchain: gcc-10, target_arch: mips, kernel_image: vmlinux, kconfig: [malta_defconfig, "https://storage.tuxboot.com/mips64/malta_defconfig"]}
  test: {device: qemu-mips64, tests: [ltp-smoke]}
- name: mips64el
  builds:
    - {toolchain: gcc-8, target_arch: mips, kernel_image: vmlinux, kconfig: [malta_defconfig, "https://storage.tuxboot.com/mips64el/malta_defconfig"]}
    - {toolchain: gcc-9, target_arch: mips, kernel_image: vmlinux, kconfig: [malta_defconfig, "https://storage.tuxboot.com/mips64el/malta_defconfig"]}
    - {toolchain: gcc-10, target_arch: mips, kernel_image: vmlinux, kconfig: [malta_defconfig, "https://storage.tuxboot.com/mips64el/malta_defconfig"]}
  test: {device: qemu-mips64el, tests: [ltp-smoke]}
- name: ppc64
  builds:
    - {toolchain: gcc-8, target_arch: powerpc, kernel_image: vmlinux, kconfig: pseries_defconfig}
    - {toolchain: gcc-9, target_arch: powerpc, kernel_image: vmlinux, kconfig: pseries_defconfig}
    - {toolchain: gcc-10, target_arch: powerpc, kernel_image: vmlinux, kconfig: pseries_defconfig}
    - {toolchain: gcc-11, target_arch: powerpc, kernel_image: vmlinux, kconfig: pseries_defconfig}
    - {toolchain: clang-nightly, target_arch: powerpc, kernel_image: vmlinux, kconfig: pseries_defconfig}
  test: {device: qemu-ppc64, tests: [ltp-smoke]}
- name: riscv64
  builds:
    - {toolchain: gcc-8, target_arch: riscv, kernel_image: Image, kconfig: defconfig}
    - {toolchain: gcc-9, target_arch: riscv, kernel_image: Image, kconfig: defconfig}
    - {toolchain: gcc-10, target_arch: riscv, kernel_image: Image, kconfig: defconfig}
    - {toolchain: gcc-11, target_arch: riscv, kernel_image: Image, kconfig: defconfig}
    - {toolchain: clang-10, target_arch: riscv, kernel_image: Image, kconfig: defconfig}
    - {toolchain: clang-11, target_arch: riscv, kernel_image: Image, kconfig: defconfig}
    - {toolchain: clang-12, target_arch: riscv, kernel_image: Image, kconfig: defconfig}
    - {toolchain: clang-nightly, target_arch: riscv, kernel_image: Image, kconfig: defconfig}
  test: {device: qemu-riscv64, tests: [ltp-smoke]}
- name: sparc64
  builds:
    - {toolchain: gcc-8, target_arch: sparc, kernel_image: vmlinux, kconfig: [sparc64_defconfig]}
    - {toolchain: gcc-9, target_arch: sparc, kernel_image: vmlinux, kconfig: [sparc64_defconfig]}
    - {toolchain: gcc-10, target_arch: sparc, kernel_image: vmlinux, kconfig: [sparc64_defconfig]}
    - {toolchain: gcc-11, target_arch: sparc, kernel_image: vmlinux, kconfig: [sparc64_defconfig]}
  test: {device: qemu-sparc64, tests: [ltp-smoke]}
- name: x86_64
  builds:
    - {toolchain: gcc-8, target_arch: x86_64, kconfig: defconfig}
    - {toolchain: gcc-9, target_arch: x86_64, kconfig: defconfig}
    - {toolchain: gcc-10, target_arch: x86_64, kconfig: defconfig}
    - {toolchain: gcc-11, target_arch: x86_64, kconfig: defconfig}
    - {toolchain: clang-10, target_arch: x86_64, kconfig: defconfig}
    - {toolchain: clang-11, target_arch: x86_64, kconfig: defconfig}
    - {toolchain: clang-12, target_arch: x86_64, kconfig: defconfig}
    - {toolchain: clang-nightly, target_arch: x86_64, kconfig: defconfig}
  test: {device: qemu-x86_64, tests: [ltp-smoke]}
```

You can validate Linus Torvald's tree with:

```shell
tuxsuite plan \
    --git-repo https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git \
    --git-ref master \
    plan.yaml
```

It's also possible to only run one part of the plan:

```shell
tuxsuite plan \
    --git-repo https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git \
    --git-ref master \
    --job-name riscv64 \
    plan.yaml
```
