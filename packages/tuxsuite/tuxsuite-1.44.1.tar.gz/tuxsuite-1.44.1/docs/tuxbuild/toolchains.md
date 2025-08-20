# Toolchains

`toolchain` is a required argument, and may be one of the following values:

- `gcc-8`
- `gcc-9`
- `gcc-10`
- `gcc-11`
- `gcc-12`
- `gcc-13`
- `clang-10`
- `clang-11`
- `clang-12`
- `clang-13`
- `clang-14`
- `clang-15`
- `clang-16`
- `clang-nightly`
- `clang-android`
- `rust`
- `rustgcc`
- `rustclang`
- `rustllvm`
- `llvm-17`
- `llvm-nightly`

Most toolschains are obtained from Debian and are updated on the first day of
each month, with the following exceptions:

- `clang-nightly` and `llvm-nightly` comes from
  [apt.llvm.org](https://apt.llvm.org/) directly, and is updated daily.
- `clang-android` comes from the [Android Clang/LLVM
  Prebuilts](https://android.googlesource.com/platform/prebuilts/clang/host/linux-x86/)
  repository and is updated monthly.
- For `rust`, `rustgcc`, `rustclang` and `rustllvm`, `rustc` comes as prebuilt
  binary release from [rust-lang.org](https://rust-lang.org/), `gcc`,
  `clang` and `llvm` comes from Debian, and they are updated monthly.

## Examples

### `tuxsuite build`

Perform an arm64 tinyconfig build against mainline using the most recent
nightly version of Clang.

```sh
tuxsuite build \
--git-repo 'https://github.com/torvalds/linux.git' \
--git-ref master \
--target-arch arm64 \
--toolchain clang-nightly \
--kconfig tinyconfig
```
