# Additional Arguments

## callback

`--callback` is an optional argument which POSTs JSON data that has
the status of the test, at the end of the test to the given URL. The
URL should be a valid http(s) link that accepts POST data.

[See Callbacks Reference, for more details](../../callbacks.md)

## callback header

`--callback-header` is an optional argument to test `submit`
subcommand through which the user can supply extra header to include
in the POST request sent to the callback URL. The header string should
be a key value pair separated by a ':' (colon). This option can be
used multiple times to add multiple headers. This option depends on
the `--callback` option.

Example:

```sh
tuxsuite test submit \
--device qemu-sh4 \
--kernel https://storage.tuxboot.com/sh4/zImage \
--callback https://tuxapi.tuxsuite.com/v1/test_callback \
--callback-header "X-First-Name: Senthil" \
--callback-header "X-Last-Name: Kumaran" \
--callback-header "X-Initial: S"
```

## host

`host` is an optional argument which allows user to run the test on a different host Runner. Valid values are 'x86_64', 'm6a.large', 'm6id.large', 'm7g.large', 'm7gd.large'. 'x86_64' is the default value.

* **x86_64 is 2vCPU + 4GB RAM with swap**
* **m6a.large is 2vCPU + 8GB RAM with no swap**
* **m7g.large is 2vCPU + 8GB RAM with no swap**
* **m6id.large is 2vCPU + 8GB RAM with NVMe disk and no swap**
* **m7gd.large is 2vCPU + 8GB RAM with NVMe disk and no swap**

```
tuxsuite test --device qemu-armv7 --kernel https://storage.tuxboot.com/armv7/zImage --tests boot,ltp-smoke --host x86_64_large
```

## notify-email

`--notify-email` or `-E` is an optional argument which sends the
result of the test, at the end of the test to the given email
address. This option can be used multiple times to add multiple email
addresses to notify.

```sh
tuxsuite test submit \
--device qemu-sh4 \
--kernel https://storage.tuxboot.com/sh4/zImage \
-E test-1@linaro.org \
--notify-email test-2@linaro.org
```
