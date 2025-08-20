# Git Repo

`git-repo` is a required argument, and should be an `https` url to a
git repository.

## Examples

### `tuxsuite build`

Perform an i386 tinyconfig build against mainline using gcc-9.

```sh
tuxsuite build \
--git-repo 'https://github.com/torvalds/linux.git' \
--git-ref master \
--target-arch i386 \
--toolchain gcc-9 \
--kconfig tinyconfig
```
