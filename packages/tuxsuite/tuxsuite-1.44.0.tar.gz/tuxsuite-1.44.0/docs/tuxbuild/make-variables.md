# Make Variables

The make variables argument is an optional positional set of arguments that
accepts key value pairs that are passed through as make variables to the build.

The set of available make variables is limited to the following.

- `C`
- `W`
- `LLVM`
- `LLVM_IAS`
- `LD`
- `AR`
- `NM`
- `STRIP`
- `OBJCOPY`
- `OBJDUMP`
- `READELF`
- `HOSTAR`
- `HOSTLD`

## Examples

### `tuxsuite build`

Example:

```
tuxsuite build \
--git-repo https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git \
--git-ref master \
--target-arch arm \
--toolchain clang-10 \
--kconfig tinyconfig \
W=1 LLVM=1
```
