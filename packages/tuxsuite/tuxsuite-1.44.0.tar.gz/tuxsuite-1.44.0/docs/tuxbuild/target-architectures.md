# Target Architectures

`target-arch` is a required argument, and defines the architecture of
the resulting kernel. It may be one of the following:

- `i386`
- `x86_64`
- `arm`
- `arm64`
- `mips`
- `riscv`
- `arc`
- `s390`
- `powerpc`
- `sparc`
- `parisc`
- `sh`
- `hexagon`
- `um`
- `m68k`
- `loongarch`

Each architecture will be built from an x86_64 host.

## Examples

### `tuxsuite build`

Perform a powerpc tinyconfig build against mainline using the most recent
nightly version of Clang.

```sh
tuxsuite build \
--git-repo 'https://github.com/torvalds/linux.git' \
--git-ref master \
--target-arch powerpc \
--toolchain clang-nightly \
--kconfig tinyconfig
```
