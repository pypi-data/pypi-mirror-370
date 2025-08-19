# Kernel Patch Series

The `--patch-series` or `-p` options accept a kernel patch series
which will be applied over the kernel source tree before starting the
build. The user should ensure that the patch series supplied is valid
and applies cleanly on the requested kernel source tree.

**ATTENTION:** <em>***In order to comply with the GPL, a patch series that is
supplied will be published together with the build artifacts
(i.e. users who have access to the binaries must also have access to
the corresponding source).*** Source and binary artifacts are removed
from the TuxSuite publication server after three months. If you are
redistributing the binaries built by TuxBuild, you must also publish
the complete corresponding source code alongside the binaries in order
to comply with the GPL.

The build artifacts URL is unique and random, and cannot be
guessed. The only users who can access the build artifacts are:

- The user who submitted the build(s), as the URLs is displayed to
  them in the terminal output.
- Other users in the same TuxSuite group (e.g. same company).
- Anyone with whom the build artifacts URL is shared.

If you are concerned with the privacy of your builds, **do not share
their URLs** with people outside of your organization.
</em>

The filename of the patch series file that was used during the build
is referenced in the `"kernel_patch_file"` field in the `status.json`
file, available in the published build artifacts directory.

Four formats are supported for kernel patch series:

- mbox
- directory
- gzipped tar archive (.tar.gz)
- an individual patch file

> **_NOTE:_** For directory and .tar.gz patch series the contents
> should contain a valid `series` file.

## Examples

### `tuxsuite build`

#### Build with mbox patch series

Perform an arm64 tinyconfig build using gcc-9 applying the given mbox
patch series on the kernel source tree at master before the build.

```sh
tuxsuite build \
--git-repo https://github.com/torvalds/linux.git \
--git-ref master \
--target-arch arm64 \
--toolchain gcc-9 \
--kconfig tinyconfig \
--patch-series /tmp/PATCH-v10-mm-slub-move-sysfs-slab-alloc-free-interfaces-to-debugfs.mbox
```

#### Build with patch series from directory

Perform an arm64 tinyconfig build using gcc-9 applying the given patch
series from directory on the kernel source tree at the specific
reference tag before the build.

```sh
tuxsuite build \
--git-repo https://kernel.googlesource.com/pub/scm/linux/kernel/git/stable/linux-stable \
--git-ref v5.10.42 \
--target-arch arm64 \
--toolchain gcc-9 \
--kconfig tinyconfig \
--patch-series /tmp/kernel-src/stable-queue/releases/5.10.43/
```

#### Build with patch series from gzipped tar archive

Perform an arm64 tinyconfig build using gcc-9 applying the given patch
series from gzipped tar archive (.tar.gz) on the kernel source tree at
the specific reference tag before the build.

```sh
tuxsuite build \
--git-repo https://kernel.googlesource.com/pub/scm/linux/kernel/git/stable/linux-stable \
--git-ref v5.10.42 \
--target-arch arm64 \
--toolchain gcc-9 \
--kconfig tinyconfig \
--patch-series /tmp/5.10.43.tar.gz
```

#### Build with patch series from URL

Perform an arm64 tinyconfig build using gcc-9 applying the given patch
series from the given URL on the kernel source tree at the specific
reference tag before the build.

```sh
tuxsuite build \
--git-repo https://kernel.googlesource.com/pub/scm/linux/kernel/git/stable/linux-stable/ \
--git-ref v5.10.42 \
--target-arch arm64 \
--toolchain gcc-9 \
--kconfig tinyconfig \
--patch-series https://www.example.com/5.10.43.tgz
```

#### Build with patch series from lore.kernel.org URL

Perform an arm64 tinyconfig build using gcc-9 applying the given patch
series from lore.kernel.org URL on the kernel source tree at the specific
reference tag before the build. In this case, if `b4` is installed in
the user's machine, then tuxsuite will download the patch series from
lore.kernel.org and use it. Attempt to use `b4` is available only for
<https://lore.kernel.org/> URL.

```sh
tuxsuite build \
--git-repo https://github.com/torvalds/linux.git \
--git-ref master \
--target-arch arm64 \
--toolchain gcc-9 \
--kconfig tinyconfig \
--patch-series https://lore.kernel.org/lkml/YmkO7LDc0q38VFlE@kroah.com/raw
```

#### Build with patch series from lore.kernel.org message-id

Perform an arm64 tinyconfig build using gcc-9 applying the given patch
series from lore.kernel.org message-id on the kernel source tree at
the specific reference tag before the build. In this case, if `b4` is
installed in the user's machine, then tuxsuite will download the patch
series from lore.kernel.org and use it. Attempt to use `b4` is
available only for <https://lore.kernel.org/> based message-id.

```sh
tuxsuite build \
--git-repo https://github.com/torvalds/linux.git \
--git-ref master \
--target-arch arm64 \
--toolchain gcc-9 \
--kconfig tinyconfig \
--patch-series 20220720131221.azqfidkry3cwiarw@bogus
```
