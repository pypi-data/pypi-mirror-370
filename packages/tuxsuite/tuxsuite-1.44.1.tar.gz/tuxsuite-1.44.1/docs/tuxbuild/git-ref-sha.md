# Git Ref and Git SHA

Either `git-ref` or `git-sha` must be specified.

If `git-ref` is specified, the branch name or tag name will be checked
out and built.

If `git-sha` is specified, the specific commit will be checked out and
built. Partial SHAs are not allowed - it must be a full 40-character
git SHA.

## Examples

### `tuxsuite build`

#### Build using `git-sha`

Perform an x86_64 defconfig build using clang-12 against a specific git SHA.

```sh
tuxsuite build \
--git-repo 'https://github.com/torvalds/linux.git' \
--git-sha f40ddce88593482919761f74910f42f4b84c004b \
--target-arch x86_64 \
--toolchain clang-12 \
--kconfig defconfig
```

#### Build using `git-ref`

Perform an x86_64 defconfig build using clang-12 against a specific git tag.

```sh
tuxsuite build \
--git-repo 'https://github.com/torvalds/linux.git' \
--git-ref v5.11 \
--target-arch x86_64 \
--toolchain clang-12 \
--kconfig defconfig
```
