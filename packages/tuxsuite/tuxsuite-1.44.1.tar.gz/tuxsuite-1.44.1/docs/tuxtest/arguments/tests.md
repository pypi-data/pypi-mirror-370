# Tests

`tests` is an optional argument that may be passed to specify the tests to run.

The argument should a comma-seperated list of tests. Available tests are:

* `binder`
* `bionic`
* `boottest`
* `boringssl`
* `compartment`
* `device-tree`
* `dvfs`
* `job-definition (used only with fvp-lava device)`
* `kselftest-gpio`
* `kselftest-ipc`
* `kselftest-ir`
* `kselftest-kcmp`
* `kselftest-kexec`
* `kselftest-rseq`
* `kselftest-rtc`
* `kunit`
* `libjpeg-turbo`
* `libpdfium`
* `libpng`
* `lldb`
* `logd`
* `ltp-controllers`
* `ltp-fcntl-locktests`
* `ltp-fs_bind`
* `ltp-fs_perms_simple`
* `ltp-fsx`
* `ltp-nptl`
* `ltp-smoke`
* `multicore`
* `fwts`
* `zlib`

By default, a `boot` test is always ran before the tests specified on the command line.

## Example

Perform boot and ltp-smoke tests on a `qemu-x86_64`.

```sh
tuxsuite test \
--device qemu-x86_64 \
--kernel https://storage.tuxboot.com/x86_64/bzImage \
--tests ltp-smoke
```
