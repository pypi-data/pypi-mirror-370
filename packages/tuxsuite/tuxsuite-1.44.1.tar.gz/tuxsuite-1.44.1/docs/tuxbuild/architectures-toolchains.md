# Architecture and Toolchain Matrix

The following combinations of architecture and toolchain are supported.

|               | i386 | x86_64 | arm | arm64 | mips | riscv | arc | s390 | powerpc | sparc | parisc | sh  | hexagon | um  | m68k | loongarch |
| ------------- | ---- | ------ | --- | ----- | ---- | ----- | --- | ---- | ------- | ----- | ------ | --- | ------- | --- | ---- | --------- |
| gcc-8         | yes  | yes    | yes | yes   | yes  | yes   | yes | yes  | yes     | yes   | yes    | yes | no      | yes | no   | no        |
| gcc-9         | yes  | yes    | yes | yes   | yes  | yes   | yes | yes  | yes     | yes   | yes    | yes | no      | yes | no   | no        |
| gcc-10        | yes  | yes    | yes | yes   | yes  | yes   | no  | yes  | yes     | yes   | yes    | yes | no      | yes | no   | no        |
| gcc-11        | yes  | yes    | yes | yes   | no   | yes   | no  | yes  | yes     | yes   | yes    | yes | no      | yes | no   | no        |
| gcc-12        | yes  | yes    | yes | yes   | yes  | yes   | no  | yes  | yes     | no    | no     | no  | no      | yes | yes  | no        |
| gcc-13        | yes  | yes    | yes | yes   | no   | yes   | no  | yes  | yes     | no    | no     | no  | no      | yes | no   | no        |
| clang-10      | yes  | yes    | yes | yes   | yes  | yes   | no  | yes  | yes     | no    | no     | no  | yes     | yes | no   | no        |
| clang-11      | yes  | yes    | yes | yes   | yes  | yes   | no  | yes  | yes     | no    | no     | no  | yes     | yes | no   | no        |
| clang-12      | yes  | yes    | yes | yes   | yes  | yes   | no  | yes  | yes     | no    | no     | no  | yes     | yes | no   | no        |
| clang-13      | yes  | yes    | yes | yes   | yes  | yes   | no  | yes  | yes     | no    | no     | no  | yes     | yes | no   | no        |
| clang-14      | yes  | yes    | yes | yes   | yes  | yes   | no  | yes  | yes     | no    | no     | no  | yes     | yes | no   | no        |
| clang-15      | yes  | yes    | yes | yes   | yes  | yes   | no  | yes  | yes     | no    | no     | no  | yes     | yes | no   | no        |
| clang-16      | yes  | yes    | yes | yes   | yes  | yes   | no  | yes  | yes     | no    | no     | no  | yes     | yes | no   | no        |
| clang-17      | yes  | yes    | yes | yes   | yes  | yes   | no  | yes  | yes     | no    | no     | no  | yes     | yes | no   | no        |
| clang-nightly | yes  | yes    | yes | yes   | yes  | yes   | no  | yes  | yes     | no    | no     | no  | yes     | yes | no   | yes       |
| clang-android | yes  | yes    | yes | yes   | no   | yes   | no  | no   | no      | no    | no     | no  | yes     | yes | no   | no        |
| rust          | no   | yes    | yes | yes   | no   | yes   | no  | no   | yes     | no    | no     | no  | no      | yes | no   | no        |
| rustgcc       | no   | yes    | yes | yes   | no   | yes   | no  | no   | yes     | no    | no     | no  | no      | no  | no   | no        |
| rustllvm      | no   | yes    | yes | yes   | no   | yes   | no  | no   | yes     | no    | no     | no  | no      | no  | no   | no        |
| rustclang     | no   | yes    | yes | yes   | no   | yes   | no  | no   | yes     | no    | no     | no  | no      | no  | no   | no        |
| llvm-17       | yes  | yes    | yes | yes   | yes  | yes   | no  | yes  | yes     | no    | no     | no  | yes     | yes | no   | no        |
| llvm-nightly  | yes  | yes    | yes | yes   | yes  | yes   | no  | yes  | yes     | no    | no     | no  | yes     | yes | no   | yes       |

This can be retrieved programmatically with the following command:

```
curl -s "https://tuxapi.tuxsuite.com/v1/supportmatrix"
```
