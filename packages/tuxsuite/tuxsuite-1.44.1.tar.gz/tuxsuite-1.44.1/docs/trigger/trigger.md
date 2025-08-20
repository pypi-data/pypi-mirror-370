# Trigger

The `trigger` sub-command provides a way to manage per-project [tuxtrigger](https://learn.tuxsuite.com/tuxtrigger/introduction/){target=_blank}
config and plan files in TuxSuite. Tuxtrigger running in the cloud will use these
config and plans to automatically track a set of git repositories and branches
when a change occurs. TuxTrigger will build, test and track the results using TuxSuite and SQUAD.
The tuxtrigger on the cloud feature is available to the community users. This sub-command
supports the following operations:

## add

The `add` sub-sub-command is used to add new plan file or folder containing multiple
plan(.yaml) files with the `--plan` option. Config file can be added
using the `--config` option.

!!! note "Config/Plan file"
    Only plan/config files with the .yaml extension is supported.

!!! info "example usage"

    * Add config and plan file

    ```shell
    tuxsuite trigger add --config /path/to/config.yaml --plan path/to/plan/file/or/directory
    ```

    * Add only the config file

    ```shell
    tuxsuite trigger add --config /path/to/config.yaml
    ```

    * Add only the plan files

    ```shell
    tuxsuite trigger add --plan /path/to/plan/file/or/directory
    ```

In the above command, config file is passed by specifying `--config` option
and `--plan` option is used to specify a plan file path or directory.
The `add` sub-sub-command can be used to upload both config file and plans simultaneously
or can also be uploaded separately.
The group and project is obtained from the config file `~/.config/tuxsuite/config.ini` or the `GROUP` and `PROJECT`
environment variables.

!!! note
    Adding a config file once again for the same group/project will overwrite the existing one. Similarly, adding a plan file with the same name will overwrite the existing plan file.

## delete

The `delete` sub-sub-command is used to delete an already available config
file or plan file or both from a project. Since there will be one config file per-project,
specifying `--config` option in the delete sub-sub-command will delete the config file.
The plan name should be given to the `--plan` option in order to delete a plan file.
The `--plan` option can be specified multiple times to delete multiple plan files.

!!! info "example usage"

    * Delete only the config file

    ```shell
    tuxsuite trigger delete --config
    ```

    * Delete a plan file

    ```shell
    tuxsuite trigger delete --plan plan-file-name
    ```

    * Delete config and plan files

    ```shell
    tuxsuite trigger delete --config --plan plan-file-1 --plan plan-file-2
    ```

!!! note
    Trying to delete a non-existent config or plan file in the above command will give a successful response.
    This is because the cloud provider follows an idempotent nature of operation.

## get

The `get` sub-sub-command is used to list all the available config and plan files for a
project.

!!! info "example usage"

    * Get config and all available plan files

    ```shell
    tuxsuite trigger get
    ```

    <details>
    <summary>Click to see output</summary>

    ```
    Tuxtrigger config:
    # config.yaml

    Tuxtrigger plans:
    1. linux-next-plan.yaml
    2. stable-plan.yaml
    ```

    </details>

    * Get contents of config file

    ```shell
    tuxsuite trigger get --config
    ```

    <details>
    <summary>Click to see output</summary>

    ```
    repositories:
    - branches:
    - name: xlnx_rebase_v6.1_LTS
        plan: stable.yaml
        squad_project: xlnx_rebase_v6.1_LTS
    - name: xlnx_rebase_v5.15_LTS
        plan: stable.yaml
        squad_project: xlnx_rebase_v5.15_LTS
    squad_group: xilinx-lts
    url: https://github.com/Xilinx/linux-xlnx
    - branches:
    - name: for-next/acpi
        plan: stable_next.yaml
        squad_project: generator-linux-for-next-acpi
    default_plan: linux_next.yaml
    squad_group: ~alok.ranjan
    url: https://git.kernel.org/pub/scm/linux/kernel/git/arm64/linux.git
    ```

    </details>

    * Get contents of plan file

    ```shell
    tuxsuite trigger get --plan plan-filename.yaml
    ```

    <details>
    <summary>Click to see output</summary>

    ```
    name: stable_plan
    version: 1
    description: stable_plan
    jobs:
    - builds:
    - kconfig: xilinx_zynqmp_defconfig
        target_arch: arm64
        toolchain: gcc-10
    - kconfig: xilinx_zynqmp_defconfig
        target_arch: arm64
        toolchain: gcc-11
    - kconfig: xilinx_zynqmp_defconfig
        target_arch: arm64
        toolchain: gcc-12
    - kconfig: xilinx_zynqmp_defconfig
        target_arch: arm64
        toolchain: clang-16
    name: xilinx-lts
    tests:
    - device: xilinx-zcu102
        dtb: xilinx/zynqmp-zcu102-rev1.0.dtb
        rootfs: https://people.linaro.org/~vishal.bhoj/zcu102-ext4.img.bz2
    - device: kv260
        dtb: xilinx/zynqmp-sm-k26-revA-sck-kv-g-revA.dtb
        rootfs: https://people.linaro.org/~vishal.bhoj/kv260/rebuilt-2022.2-kv260/petalinux-hacked-minimal-kv260-starter-kit.wic.xz
    ```

    </details>
