# Building Mbed-TLS for one configuration

Submit an Mbed-TLS build request using the tuxsuite command line interface. This will
wait for the build to complete before returning by default.

```shell
git clone https://gitlab.com/Linaro/tuxsuite
cd tuxsuite
tuxsuite bake submit examples/bitbake/mbed.yaml
```

The results
([build-definition.yaml](https://storage.tuxsuite.com/public/demo/demo/oebuilds/31UIIgJzRHFtfAvTcpUi1PTZMYF/build-definition.yaml),
[logs](https://storage.tuxsuite.com/public/demo/demo/oebuilds/31UIIgJzRHFtfAvTcpUi1PTZMYF/build.log), ...)
will be available at
[artifacts](https://storage.tuxsuite.com/public/demo/demo/oebuilds/31UIIgJzRHFtfAvTcpUi1PTZMYF/)
under a unique and non-guessable URL.

## Build definition

Mbed-TLS uses build-definition to describe the build:
!!! info "Using repo"

    ```yaml
    container: tuxbake/mbedtls-ubuntu-16.04
    sources:
      mbedtls:
        url: https://github.com/Mbed-TLS/mbedtls
        branch: master
        cmds: ulimit -f 20971520 && export MBEDTLS_TEST_OUTCOME_FILE='outcome.csv' &&
          ./tests/scripts/all.sh --seed 8 build_armcc
    ```

### Build definition format

The build definition can include the following fields:

* `sources` (dictionary with a single item): should be mbedtls. url, branch or ref can be specified. cmds is the command used to do the specific build.
* `container`: Docker container used to do the build. Currently provided containers are tuxbake/mbedtls-ubuntu-16.04, tuxbake/mbedtls-ubuntu-18.04, tuxbake/mbedtls-ubuntu-20.04.

### Plan

The plan that does all the builds corresponding to CI for mbed-TLS for Linux is available in [mbed.yaml](https://gitlab.com/Linaro/tuxsuite/-/blob/master/examples/bitbake/mbed.yaml)

The result of the above plan that has done the full build is available in [mbed-results](https://tuxapi.tuxsuite.com/v1/groups/demo/projects/demo/plans/2KReAZr8wxioSqPzr2Fnst8gaop)
