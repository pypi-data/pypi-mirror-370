# Environment Variables

The environment argument accepts a key value pair that is used to pass
the environment variables that will be set during the build.

Passing `-e`/`--enviroment` to `build` will set the environment
variables during build time. There could be multiple environment
variables passed via this argument.

There is a minimal set of environment variables that are
supported. Arbitrary environment variables cannot be supplied, except
for the ones listed below:

- KCONFIG_ALLCONFIG

## Examples

### `tuxsuite build`

Set KCONFIG_ALLCONFIG in an arm64 allmodconfig build.

```
tuxsuite build \
--git-repo https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git \
--git-ref master \
--target-arch arm64 \
--toolchain clang-10 \
--kconfig allmodconfig \
--environment KCONFIG_ALLCONFIG=arch/arm64/configs/defconfig
```
