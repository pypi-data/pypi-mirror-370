# Python client API

The tuxsuite client can also be used from Python programs. The authentication
token needs to be in place in `~/.config/tuxsuite/config.ini`, or via the
`$TUXSUITE_TOKEN` environment variable.

## Single builds

```python
import tuxsuite

params = {
    "git_repo": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
    "git_ref": "master",
    "target_arch": "arm64",
    "toolchain": "gcc-9",
    "kconfig": [
      "defconfig"
    ],
}

# fire and forget
build = tuxsuite.Build(**params)
build.build()

# submit a build and wait for it to finish, quietly
build = tuxsuite.Build(**params)
build.build()
state = build.wait()
print(f"{state.icon} #{build}: #{state.message}")

# submit build and watch its progress
build = tuxsuite.Build(**params)
build.build()
for state in build.watch():
  print(f"{state.icon} #{build}: #{state.message}")
```

## Single tests

```python
import tuxsuite

params = {
    "device": "qemu-x86_64",
    "kernel": "https://storage.tuxboot.com/x86_64/bzImage",
    "tests": ["ltp-smoke"],
}

# fire and forget
test = tuxsuite.Test(**params)
test.test()

# submit a test and wait for it to finish, quietly
test = tuxsuite.Test(**params)
test.test()
state = test.wait()
print(f"{state.icon} #{build}: #{state.message}")

# submit test and watch its progress
test = tuxsuite.Test(**params)
test.test()
for state in test.watch():
  print(f"{state.icon} #{test}: #{state.message}")
```
