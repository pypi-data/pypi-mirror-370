# Examples

## Complete Flow

A build/test/plan that was submitted by `tuxsuite` command
can output a JSON file capturing the details of the submitted
action. When combined with the `--no-wait` option, the submission will
return immediately and the captured JSON output can be used to fetch
the results of the particular action, which is illustrated in the
following examples.

### Build

This will submit a `build` with `--no-wait` and capture the build
artifacts in a JSON file.

```shell
tuxsuite build \
    --git-repo https://github.com/torvalds/linux.git \
    --git-ref master --target-arch arm64 --toolchain gcc-10 \
    --kconfig tinyconfig \
    --no-wait \
    --json-out /tmp/build_status.json
```

The above build will get submitted and returns instantaneously
capturing the build artifacts in `/tmp/build_status.json` whose output
looks like the following,

```json
{
    "build_name": "",
    "client_token": "7a7a4058-2014-403c-bbef-bcb12c898894",
    "download_url": "https://builds.tuxbuild.com/1t2X8ddYei4bhGlsscUJv46woGi/",
    "environment": {},
    "errors_count": 0,
    "finished_time": null,
    "git_ref": "master",
    "git_repo": "https://github.com/torvalds/linux.git",
    "git_sha": "ad9f25d338605d26acedcaf3ba5fab5ca26f1c10",
    "kconfig": [
        "tinyconfig"
    ],
    "kernel_image": "",
    "make_variables": {},
    "plan": null,
    "project": "tuxsuite/senthil",
    "provisioning_time": "2021-05-25T18:39:59.723270",
    "result": "unknown",
    "running_time": null,
    "state": "provisioning",
    "target_arch": "arm64",
    "targets": [],
    "toolchain": "gcc-10",
    "uid": "1t2X8ddYei4bhGlsscUJv46woGi",
    "user": "senthil.kumaran@linaro.org",
    "waited_by": [],
    "warnings_count": 0
}
```

`/tmp/build_status.json` JSON file generated above can be used to
fetch the result of the build at a later point of time, using the
`results` sub-command of `tuxsuite` CLI.

```shell
tuxsuite results \
    --from-json /tmp/build_status.json \
    --json-out /tmp/build_result.json
```

The above command can capture the results of the build, once again
into a JSON file using the `--json-out` option. The captured JSON is
shown below, which will have the build result with details after the
completion of the build, if invoked after sometime when the build
completes.

```shell
{
    "build_name": "",
    "build_status": "pass",
    "client_token": "7a7a4058-2014-403c-bbef-bcb12c898894",
    "download_url": "https://builds.tuxbuild.com/1t2X8ddYei4bhGlsscUJv46woGi/",
    "duration": 113,
    "environment": {},
    "errors_count": 0,
    "finished_time": "2021-05-25T18:43:57.519607",
    "git_describe": "v5.13-rc3-43-gad9f25d33860",
    "git_ref": "master",
    "git_repo": "https://github.com/torvalds/linux.git",
    "git_sha": "ad9f25d338605d26acedcaf3ba5fab5ca26f1c10",
    "git_short_log": "ad9f25d33860 (\"Merge tag 'netfs-lib-fixes-20200525' of git://git.kernel.org/pub/scm/linux/kernel/git/dhowells/linux-fs\")",
    "kconfig": [
        "tinyconfig"
    ],
    "kernel_image": "",
    "kernel_image_name": "Image.gz",
    "kernel_version": "5.13.0-rc3",
    "make_variables": {},
    "plan": null,
    "project": "tuxsuite/senthil",
    "provisioning_time": "2021-05-25T18:39:59.723270",
    "result": "pass",
    "running_time": "2021-05-25T18:42:06.263535",
    "sccache_hits": 662,
    "sccache_misses": 1,
    "state": "finished",
    "status_message": "build completed",
    "target_arch": "arm64",
    "targets": [],
    "toolchain": "gcc-10",
    "tuxbuild_status": "complete",
    "uid": "1t2X8ddYei4bhGlsscUJv46woGi",
    "user": "senthil.kumaran@linaro.org",
    "waited_by": [],
    "warnings_count": 0
}
```

### Test

This will submit a `test` with `--no-wait` and capture the `test`
artifacts in a JSON file.

```shell
tuxsuite test \
    --device qemu-arm \
    --kernel https://builds.dev.tuxbuild.com/1sAr4I924g9JSt1bIVKs3kz1wKS/zImage \
    --no-wait \
    --json-out /tmp/test_status.json
```

The above test will get submitted and returns instantaneously
capturing the test artifacts in `/tmp/test_status.json` whose output
looks like the following,

```json
{
    "boot_args": null,
    "device": "qemu-armv7",
    "finished_time": null,
    "kernel": "https://builds.dev.tuxbuild.com/1sAr4I924g9JSt1bIVKs3kz1wKS/zImage",
    "modules": null,
    "plan": null,
    "project": "tuxsuite/senthil",
    "provisioning_time": "2021-05-25T18:59:14.038481",
    "result": "unknown",
    "results": {},
    "running_time": null,
    "state": "provisioning",
    "tests": [
        "boot"
    ],
    "uid": "1t2ZTkuRNcNx0xEg1NlI9ScxYQA",
    "waiting_for": null
}
```

`/tmp/test_status.json` JSON file generated above can be used to
fetch the result of the test at a later point of time, using the
`results` sub-command of `tuxsuite` CLI.

```shell
tuxsuite results \
    --from-json /tmp/test_status.json \
    --json-out /tmp/test_result.json
```

The above command can capture the results of the test, once again
into a JSON file using the `--json-out` option. The captured JSON is
shown below, which will have the test result with details after the
completion of the test, if invoked after sometime when the test
completes.

```shell
{
    "boot_args": null,
    "device": "qemu-arm64",
    "duration": 211,
    "finished_time": "2021-05-03T15:31:01.898530",
    "kernel": "https://builds.stylesen.dev.tuxbuild.com/1s1wqDrm5cHNac7Ik9Q6h9ixBIa/Image.gz",
    "modules": null,
    "plan": null,
    "project": "tuxsuite/senthil",
    "provisioning_time": "2021-05-03T15:24:26.069241",
    "result": "fail",
    "results": {
        "boot": "fail"
    },
    "running_time": "2021-05-03T15:27:32.223893",
    "state": "finished",
    "tests": [
        "boot"
    ],
    "uid": "1s20dnMkE94e3BHW8pEbOWuyL6z",
    "waiting_for": null
}
```

### Plan

This will submit a `plan` with `--no-wait` and capture the `plan`
artifacts in a JSON file.

```shell
tuxsuite plan \
    --git-repo https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git \
    --git-ref master examples/planv1.yaml \
    --no-wait
```

The above `plan` will get submitted and returns instantaneously due to
the usage of `--no-wait` option. The output will have the submitted
plan's UID which can be used to fetch the results later.

```shell
tuxsuite results --plan 1t2aIHdTp3VllMHawJ9lt9myUge
```

The `--json-out` option can be used to capture the plan's result in
JSON format, which will have the plan results with details after the
completion of the plan, if invoked after sometime when the plan
completes.

```shell
tuxsuite results --plan 1t2aIHdTp3VllMHawJ9lt9myUge \
    --json-out /tmp/plan_result.json
```
