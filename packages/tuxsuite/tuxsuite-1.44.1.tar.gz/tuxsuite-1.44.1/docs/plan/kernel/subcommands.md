# Sub-commands

## cancel

`cancel` is a subcommand for cancelling submitted plan identified by its `uid`.
Cancelling is available for any build/oebuild/test state, except `finished`.

```
tuxsuite plan cancel 1t2giSA1sSKFADKPrl0YI1gjMLb
```

## get

`get` is a subcommand which fetches the details for the plan
identified by its `uid`.

```
tuxsuite plan get 1t2gzLqkWHi2ldxDETNMVHPYBYo
```

## list

`list` is a subcommand which fetches the latest 30 plans by default.

```
tuxsuite plan list
```

In order to restrict the number of plans fetched, `--limit` is used
as follows:

```
tuxsuite plan list --limit 5
```

To get the output of the above commands in JSON format, use the
following:

```
tuxsuite plan list --json --limit 2
```

## submit

`submit` is a subcommand for submitting plan files.

```
tuxsuite plan submit plan.yaml
```

## wait

`wait` is a subcommand which fetches the details for the plan identified
by its `uid`, if the plan is in progress, it will update the details
on screen. This will be handy to submit a plan and come back at a
later point of time to watch the plan's progression.

```
tuxsuite plan wait 1yiHhE3rnithNxBudqxCrWBlWKp
```

## create

`create` is a subcommand to generate a plan file from individual build/test plan file.
This subcommand takes `--build-plan` and `--test-plan` Path/URL as input to produce a plan which
consists of build from build plan file and test from test plan file. The options `--build-plan`
and `--test-plan` can be utilized either individually or in combination with other [options](#create-options)
to generate a plan.

!!! note "Note"
    This subcommand takes a build/test plan file that contains only a single build or test job

!!! info "example"

    * Generate a plan with both build and test

    ```shell
    tuxsuite plan create --build-plan <build-plan.yaml/URL> --test-plan <test-plan.yaml/URL>
    ```

    * Generate a plan from build plan

    ```shell
    tuxsuite plan create --build-plan <build-plan.yaml/URL>
    ```

    * Generate a plan from test plan

    ```shell
    tuxsuite plan create --test-plan <test-plan.yaml/URL>
    ```

### create-options

The `create` subcommand supports the following options:

* `--build-plan`: Path/URL to build plan file.
* `--test-plan`: Path/URL to test plan file.
* `--test-retrigger`: Number of times test has to be retriggered. Defaults to 1.
* `--overwrite-target`: Targets to be overwritten to build job. Specific to build plan only.
* `--append-kconfig`: Kconfig to append to build job. Specific to build plan only.
* `--output-plan`: Output plan file path.

## execute

`execute` is a subcommand to run a short and concise kernel [plan](../kernel/index.md) file locally on the host machine.
This subcommand takes plan `config file` containing builds and/or tests only. `sanity_test` is not supported.
Jobs will be executed sequentially.

!!! note "Note"
    Test jobs are run on virtual devices using [Tuxrun](https://tuxrun.org/). Physical devices are not
    supported.

!!! info "example usage"

    * Execute a plan locally.

    ```shell
    tuxsuite plan execute plan.yaml --tree <path-to-linux-source-tree>
    ```

    * Execute a specific job from the plan file

    ```shell
    tuxsuite plan execute plan.yaml --tree <path-linux-source-tree> --job-name <job-name>
    ```

### execute-options

The `execute` subcommand supports the following options:

* `--tree`: Path to the Linux kernel source tree. Defaults to current working directory.
* `-r/--runtime`: Container runtime to use. Supported runtimes are `docker` and `podman`. Defaults to `podman`.
* `--job-name`: Name of the specific job to run from the plan file. Can be specified multiple times.
* `-d/--output-dir`: Output directory to save build or test artifacts. If not specified, a temporary directory under `~/.cache/tuxsuite/plan/` will be used.
