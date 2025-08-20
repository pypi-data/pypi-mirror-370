# Device

`device` is a required argument, and may be one of the following values:

* fvp-aemva
* fvp-morello-android
* fvp-morello-busybox
* fvp-morello-baremetal
* fvp-morello-oe
* fvp-morello-ubuntu
* qemu-arm
* qemu-armv5
* qemu-armv7
* qemu-armv7be
* qemu-arm64
* qemu-arm64be
* qemu-i386
* qemu-mips
* qemu-mips32
* qemu-mips32el
* qemu-mips64
* qemu-mips64el
* qemu-mipsel
* qemu-powerpc
* qemu-ppc32
* qemu-ppc64
* qemu-ppc64le
* qemu-riscv
* qemu-riscv64
* qemu-s390
* qemu-sh4
* qemu-sparc64
* qemu-x86_64

## Examples

Perform a boot test on a `qemu-x86_64`.

```sh
tuxsuite test \
--device qemu-x86_64 \
--kernel https://storage.tuxboot.com/x86_64/bzImage
```
