# Testing on SSH Device

## Running tests on AWS Graviton Targets

TuxSuite supports running tests on AWS Graviton VM and Baremetal instances
as DUT. The target is configured to boot Debian bookworm AMI with the test kernel.

These are the available targets as ssh devices and the option needed to be passed:

| Device           | Device type |  --parameter       |
|------------------|-------------|--------------------|
| m7g.large        | ssh-device  | dut=m7g.large      |
| c7g.metal        | ssh-device  | dut=c7g.metal      |
| r8g.large        | ssh-device  | dut=r8g.large      |
| r8g.metal-24xl   | ssh-device  | dut=r8g.metal-24xl |

```shell
tuxsuite test submit --device ssh-device --boot-args rw --kernel https://storage.tuxsuite.com/public/demo/demo/builds/2jEqhbAm1NKWLjmD9LZ7bGdUAqF/Image.gz --rootfs https://storage.tuxboot.com/debian/bookworm/arm64/rootfs.ext4.xz --modules https://storage.tuxsuite.com/public/demo/demo/builds/2jEqhbAm1NKWLjmD9LZ7bGdUAqF/modules.tar.xz --parameters KSELFTEST=https://storage.tuxsuite.com/public/demo/demo/builds/2jEqhbAm1NKWLjmD9LZ7bGdUAqF/kselftest.tar.xz --parameters dut=r8g.large --tests kselftest-arm64 --timeouts boot=30 --timeouts commands=10 -- dmesg
```  

The output will look like:

```shell
Testing https://storage.tuxsuite.com/public/demo/demo/builds/2jEqhbAm1NKWLjmD9LZ7bGdUAqF/Image.gz on ssh-device with boot, kselftest-arm64
uid: 2jF6Wv5cN6lTxuwQDvWqmhL9Q2t
⚙️  Provisioning: [boot, kselftest-arm64] ssh-device @ https://tuxapi.tuxsuite.com/v1/groups/demo/projects/demo/tests/2jF6Wv5cN6lTxuwQDvWqmhL9Q2t
🚀 Running: [boot, kselftest-arm64] ssh-device @ https://tuxapi.tuxsuite.com/v1/groups/demo/projects/demo/tests/2jF6Wv5cN6lTxuwQDvWqmhL9Q2t
🎉 Pass: [boot, kselftest-arm64] ssh-device @ https://tuxapi.tuxsuite.com/v1/groups/demo/projects/demo/tests/2jF6Wv5cN6lTxuwQDvWqmhL9Q2t
```

## Running tests on GCP Axion Targets

TuxSuite supports running tests on GCP Axion VM as DUT. The target is configured to boot Debian bookworm AMI with the test kernel.

These are the available targets as ssh devices and the option needed to be passed:

| Device           | Device type |  --parameter        | Specs         |
|------------------|-------------|---------------------|---------------|
| c4a-standard-1   | ssh-device  | dut=c4a-standard-1  | 1vCPU 4GB Mem |
| c4a-standard-2   | ssh-device  | dut=c4a-standard-2  | 2vCPU 8GB Mem |

```shell
tuxsuite test submit --device ssh-device --boot-args rw --kernel https://storage.tuxsuite.com/public/demo/demo/builds/2jEqhbAm1NKWLjmD9LZ7bGdUAqF/Image.gz --rootfs https://storage.tuxboot.com/debian/bookworm/arm64/rootfs.ext4.xz --modules https://storage.tuxsuite.com/public/demo/demo/builds/2jEqhbAm1NKWLjmD9LZ7bGdUAqF/modules.tar.xz --parameters KSELFTEST=https://storage.tuxsuite.com/public/demo/demo/builds/2jEqhbAm1NKWLjmD9LZ7bGdUAqF/kselftest.tar.xz --parameters dut=c4a-standard-1 --tests kselftest-arm64 --timeouts boot=30 --timeouts commands=10 -- dmesg
```

The output will look like:

```shell
tuxsuite test submit --device ssh-device --boot-args rw --kernel https://storage.tuxsuite.com/public/demo/demo/builds/2jEqhbAm1NKWLjmD9LZ7bGdUAqF/Image.gz --rootfs https://storage.tuxboot.com/debian/bookworm/arm64/rootfs.ext4.xz --modules https://storage.tuxsuite.com/public/demo/demo/builds/2jEqhbAm1NKWLjmD9LZ7bGdUAqF/modules.tar.xz --parameters KSELFTEST=https://storage.tuxsuite.com/public/demo/demo/builds/2jEqhbAm1NKWLjmD9LZ7bGdUAqF/kselftest.tar.xz --parameters dut=c4a-standard-1 --tests kselftest-arm64 --timeouts boot=30 --timeouts commands=10 -- dmesg
Testing https://storage.tuxsuite.com/public/demo/demo/builds/2jEqhbAm1NKWLjmD9LZ7bGdUAqF/Image.gz on ssh-device with boot, kselftest-arm64
uid: 2nqGC9aYyd9CUBm2J0xY0Puer0O
⚙️  Provisioning: [boot, kselftest-arm64] ssh-device @ https://tuxapi.tuxsuite.com/v1/groups/demo/projects/demo/tests/2nqGC9aYyd9CUBm2J0xY0Puer0O
🚀 Running: [boot, kselftest-arm64] ssh-device @ https://tuxapi.tuxsuite.com/v1/groups/demo/projects/demo/tests/2nqGC9aYyd9CUBm2J0xY0Puer0O
🎉 Pass: [boot, kselftest-arm64] ssh-device @ https://tuxapi.tuxsuite.com/v1/groups/demo/projects/demo/tests/2nqGC9aYyd9CUBm2J0xY0Puer0O
```