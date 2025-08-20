# No Wait

`--no-wait` is an optional argument which submits the test and returns
immediately printing the test artifacts to `stdout`.

## Example

Perform boot and ltp-smoke tests on a `qemu-x86_64` with `no-wait`

```sh
tuxsuite test \
--device qemu-x86_64 \
--kernel https://storage.tuxboot.com/x86_64/bzImage \
--tests ltp-smoke \
--no-wait
```
