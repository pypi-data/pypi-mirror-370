# Build Name

`build-name` is an optional argument that may be passed in with each
build. If supplied, the string will be passed through to the resulting
build status.

## Examples

### `tuxsuite build`

Perform a mainline build with a descriptive build-name.

```sh
tuxsuite build \
--git-repo 'https://github.com/torvalds/linux.git' \
--git-ref master \
--target-arch arm64 \
--toolchain clang-nightly \
--kconfig tinyconfig \
--build-name "arm64 clang-nightly tinyconfig mainline"
```

The resulting `status.json` will have a `build_name` field with the desired
value passed through, excerpted below:

```json
{
    "build_key": "1oiYvkUr1ctXdkV7KCLZ6320JVw",
    "build_name": "arm64 clang-nightly tinyconfig mainline",
    "build_status": "pass",
...
```
