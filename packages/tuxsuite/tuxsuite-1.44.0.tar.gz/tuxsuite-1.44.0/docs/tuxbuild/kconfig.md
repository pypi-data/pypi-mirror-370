# Kernel Configuration

One or more `kconfig` arguments are required and are used to define what kernel
config to use.

The first argument must be a URL to a valid kconfig file or defconfig argument
that ends in "config", such as "defconfig" or "allmodconfig".

Subsequent kconfig arguments may also be provided to modify the contents of the
resulting config. There are multiple ways to specify additional configuration:

- an in-tree configuration target (e.g. `kvm_guest.config`)
- a URL to a config file, in which case it will be downloaded
- a config fragment matching one of these:
   - `CONFIG_*=[y|m|n]`
   - `# CONFIG_* is not set`

Any in-tree configuration target will be built with `make`, and then all of the
others will be saved to a local file in the order they were passed. They will
be then merged on top of the existing configuration by calling
`scripts/kconfig/merge_config.sh` and `make olddefconfig`.

## Examples

### `tuxsuite build`

Perform an arm64 build against mainline using the most recent nightly version
of Clang using defconfig plus KASAN plus a config fragment from a URL.

```sh
tuxsuite build \
--git-repo 'https://github.com/torvalds/linux.git' \
--git-ref master \
--target-arch arm64 \
--toolchain clang-nightly \
--kconfig defconfig \
--kconfig CONFIG_KASAN=y \
--kconfig "https://gist.githubusercontent.com/danrue/9e1e4d90149daadd5199256cc18a0499/raw/752138764ec039e4593185bfff888250a3d7692f/gistfile1.txt"
```
