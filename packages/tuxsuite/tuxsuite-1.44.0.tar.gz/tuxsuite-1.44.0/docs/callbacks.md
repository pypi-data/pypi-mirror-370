# Callback Support

The tuxsuite cli provides a way to push notification to a given
http(s) based URL at the end of the build/oebuild/test run. The URL
should be passed by the optional argument `--callback` as shown below:

```sh
tuxsuite build \
--git-repo https://github.com/torvalds/linux.git \
--git-ref master \
--target-arch arm \
--toolchain clang-16 \
--kconfig tinyconfig \
--callback https://tuxapi.tuxsuite.com/v1/test_callback
```

__NOTE__: The above callback URL is shown as an example and it does
not exist.

In order to get a push notification to a given http(s) based URL at
the end of a plan submission, use the `--plan-callback` optional
argument as shown below:

```sh
tuxsuite plan submit \
--plan-callback https://tuxapi.tuxsuite.com/v1/test_plan_callback \
plan-v1.yaml
```

__NOTE__: The above plan callback URL is shown as an example and it
does not exist.

To supply extra header to be included when calling the plan callback
URL use the `--plan-callback-header` option, one or more times as
shown below:

```sh
tuxsuite plan submit \
--plan-callback https://tuxapi.tuxsuite.com/v1/test_plan_callback \
--plan-callback-header "X-First-Name: Senthil" \
--plan-callback-header "X-Last-Name: Kumaran" \
plan-v1.yaml
```

## Security

The JSON data POSTed by Tux backend comes with a security feature
which allows the user to verify that the callback notification comes
from the Tux backend and not anywhere else. There is a signature which
is sent as part of the POST request header called
`x-tux-payload-signature`. This signature is base64 encoded and can be
used to verify the authenticity of the sender of the notification.

Following is the verification code in Python:

```py
import base64


from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization


def verify(public_key: str, signature: str, payload: str):
   """Function to illustrate the verification of the signature."""
   signature = base64.urlsafe_b64decode(signature)
   key = serialization.load_ssh_public_key(public_key.encode("ascii"))
       try:
           key.verify(
               signature,
               payload.encode("utf-8"),
               ec.ECDSA(hashes.SHA256()),
           )
           return True
       except InvalidSignature:
           return False
```

- **public_key**: The public key should be cached in the user's server
  that accepts the push notification. The public key for a specific Tux
  group (`tuxsuite` in this case) can be obtained as follows:

```sh
curl https://tuxapi.tuxsuite.com/v1/groups/tuxsuite/projects/demo/keys -o keys.json
```

- **signature**: This is the signature that is sent with the
  `x-tux-payload-signature` header in the request.

- **payload**: The JSON payload is sent as part of the request. The
  value of `kind` in the JSON, will be one of
  build/oebuild/test/plan. Following is a sample JSON  payload, for
  illustration:

<details>
<summary>Click to see payload sample for a build</summary>

```json
{
    "kind": "build",
    "status": {
        "auto_retry": true,
        "build_name": "",
        "build_status": "pass",
        "callback": "https://tuxapi.tuxsuite.com/v1/test_callback",
        "client_token": "82ce12c7-c41a-4ebf-9771-198b8e9e3aa2",
        "download_url": "https://storage.tuxsuite.com/public/demo/demo/builds/2ZITcwA6wxeKxh9cZA5HBJ6FkSj/",
        "duration": 258,
        "environment": {},
        "errors_count": 0,
        "finished_time": "2023-12-09T08:08:24.822016",
        "git_describe": "v6.7-rc4-111-g5e3f5b81de80",
        "git_ref": "master",
        "git_repo": "https://gitlab.com/Linaro/lkft/mirrors/stable/linux-stable-rc",
        "git_sha": "5e3f5b81de80c98338bcb47c233aebefee5a4801",
        "git_short_log": "5e3f5b81de80 (\"Merge tag 'net-6.7-rc5' of git://git.kernel.org/pub/scm/linux/kernel/git/netdev/net\")",
        "image_sha": "",
        "is_canceling": false,
        "is_public": true,
        "kconfig": [
            "tinyconfig"
        ],
        "kernel_image": "",
        "kernel_image_name": "Image.gz",
        "kernel_patch_file": "",
        "kernel_version": "6.7.0-rc4",
        "make_variables": {
            "LLVM": "1",
            "LLVM_IAS": "1"
        },
        "modules": false,
        "no_cache": false,
        "plan": null,
        "project": "demo/demo",
        "provisioning_time": "2023-12-09T07:57:56.699401",
        "result": "pass",
        "retry": 0,
        "retry_message": "",
        "running_time": "2023-12-09T08:03:50.889831",
        "sccache_hits": 643,
        "sccache_misses": 2,
        "setup_duration": 132,
        "state": "finished",
        "status_message": "build completed",
        "target_arch": "arm64",
        "targets": [],
        "token_name": "demo-tuxsuite",
        "toolchain": "clang-17",
        "tuxbuild_status": "complete",
        "tuxmake_metadata": {
            "compiler": {
                "name": "clang",
                "version": "17.0.6",
                "version_full": "Debian clang version 17.0.6 (++20231128093145+6009708b4367-1~exp1~20231128093253.72)"
            },
            "results": {
                "artifacts": {
                    "config": [
                        "config"
                    ],
                    "debugkernel": [
                        "vmlinux.xz",
                        "System.map"
                    ],
                    "default": [],
                    "dtbs": [
                        "dtbs.tar.xz"
                    ],
                    "dtbs-legacy": [
                        "dtbs.tar.xz"
                    ],
                    "headers": [
                        "headers.tar.xz"
                    ],
                    "kernel": [
                        "Image.gz"
                    ],
                    "log": [
                        "build.log",
                        "build-debug.log"
                    ],
                    "modules": [],
                    "xipkernel": []
                },
                "duration": {
                    "build": 53.78269052505493,
                    "cleanup": 0.34334325790405273,
                    "copy": 0.021654129028320312,
                    "metadata": 0.8076236248016357,
                    "prepare": 142.58426547050476,
                    "validate": 0.00023031234741210938
                },
                "errors": 0,
                "status": "PASS",
                "targets": {
                    "config": {
                        "duration": 9.226672887802124,
                        "status": "PASS"
                    },
                    "debugkernel": {
                        "duration": 1.036712408065796,
                        "status": "PASS"
                    },
                    "default": {
                        "duration": 30.07289409637451,
                        "status": "PASS"
                    },
                    "dtbs": {
                        "duration": 3.9019832611083984,
                        "status": "PASS"
                    },
                    "dtbs-legacy": {
                        "duration": 0.5993697643280029,
                        "status": "SKIP"
                    },
                    "headers": {
                        "duration": 5.118199825286865,
                        "status": "PASS"
                    },
                    "kernel": {
                        "duration": 2.5232584476470947,
                        "status": "PASS"
                    },
                    "modules": {
                        "duration": 0.3326840400695801,
                        "status": "SKIP"
                    },
                    "xipkernel": {
                        "duration": 0.3573451042175293,
                        "status": "SKIP"
                    }
                },
                "warnings": 0
            },
            "runtime": {
                "image_digest": "855116176053.dkr.ecr.us-east-1.amazonaws.com/tuxmake/arm64_clang-17@sha256:2de64794a3c18b331f17ee0ce9a1948450096784ec7db2e5deae089072ccbb73",
                "image_name": "855116176053.dkr.ecr.us-east-1.amazonaws.com/tuxmake/arm64_clang-17",
                "version": "podman version 4.6.2"
            },
            "tools": {
                "ar": "GNU ar (GNU Binutils for Debian) 2.35.2",
                "as": "GNU assembler (GNU Binutils for Debian) 2.35.2",
                "bc": "bc 1.07.1",
                "bison": "bison (GNU Bison) 3.7.5",
                "ccache": "ccache version 4.2",
                "clang": "Debian clang version 17.0.6 (++20231128093145+6009708b4367-1~exp1~20231128093253.72)",
                "depmod": "kmod version 28",
                "fdformat": "fdformat from util-linux 2.36.1",
                "flex": "flex 2.6.4",
                "gcc": "gcc (Debian 10.2.1-6) 10.2.1 20210110",
                "ld": "GNU ld (GNU Binutils for Debian) 2.35.2",
                "lld": "Debian LLD 17.0.6 (compatible with GNU linkers)",
                "make": "GNU Make 4.3",
                "openssl": "OpenSSL 1.1.1w  11 Sep 2023",
                "pahole": "v1.25",
                "ps": "ps from procps-ng 3.3.17",
                "sccache": "sccache 0.2.9"
            },
            "tuxmake": {
                "version": "1.20.0"
            }
        },
        "uid": "2ZITcwA6wxeKxh9cZA5HBJ6FkSj",
        "user": "demo.user@linaro.org",
        "user_agent": "tuxsuite/1.33.0",
        "waited_by": [],
        "warnings_count": 0
    }
}
```

</details>

<details>
<summary>Click to see payload sample for a test</summary>

```json
{
    "kind": "test",
    "status": {
        "ap_romfw": null,
        "bios": null,
        "bl1": null,
        "boot_args": null,
        "callback": "https://tuxapi.tuxsuite.com/v1/test_callback",
        "device": "qemu-arm64",
        "download_url": "https://storage.tuxsuite.com/public/tuxsuite/demo/tests/2MBYa8FhoBHkRCX2BMMPusjuClf/",
        "dtb": null,
        "duration": 117,
        "finished_time": "2023-02-24T12:44:23.178581",
        "fip": null,
        "is_canceling": false,
        "is_public": true,
        "kernel": "https://storage.tuxsuite.com/public/linaro/lkft/builds/2M0PXsQDVWO3DwIKTIlwtDELTpb/Image.gz",
        "mcp_fw": null,
        "mcp_romfw": null,
        "modules": "https://storage.tuxsuite.com/public/linaro/lkft/builds/2M0PXsQDVWO3DwIKTIlwtDELTpb/modules.tar.xz",
        "parameters": {
            "SHARD_INDEX": "4",
            "SHARD_NUMBER": "10",
            "SKIPFILE": "skipfile-lkft.yaml"
        },
        "plan": null,
        "project": "tuxsuite/demo",
        "provisioning_time": "2023-02-24T12:41:42.541788",
        "result": "pass",
        "results": {
            "boot": "pass"
        },
        "retries": 0,
        "retries_messages": [],
        "rootfs": "https://storage.tuxsuite.com/public/linaro/lkft/oebuilds/2LjyTGHSPqxUqtyCl1xI7SCrbWp/images/juno/lkft-tux-image-juno-20230214185536.rootfs.ext4.gz",
        "running_time": "2023-02-24T12:42:27.314447",
        "scp_fw": null,
        "scp_romfw": null,
        "state": "finished",
        "tests": [
            "boot"
        ],
        "timeouts": {},
        "token_name": "demo-tuxsuite",
        "uefi": null,
        "uid": "2MBYa8FhoBHkRCX2BMMPusjuClf",
        "user": "demo.user@linaro.org",
        "user_agent": "tuxsuite/1.9.0",
        "waiting_for": null
    }
}
```

</details>

<details>
<summary>Click to see payload sample for a oebuild</summary>

```json
{
    "kind": "oebuild",
    "status": {
        "artifacts": [],
        "bblayers_conf": [],
        "callback": "https://tuxapi.tuxsuite.com/v1/test_callback",
        "container": "ubuntu-20.04",
        "distro": "oniro-linux",
        "download_url": "https://storage.tuxsuite.com/public/demo/demo/oebuilds/2ZITcWtwDj3povtoSM0c5sk30FZ/",
        "duration": 127,
        "environment": {
            "TEMPLATECONF": "../oniro/flavours/linux"
        },
        "envsetup": "oe-core/oe-init-build-env",
        "errors_count": 0,
        "extraconfigs": [],
        "finished_time": "2023-12-09T08:02:19.569984",
        "is_canceling": false,
        "is_public": true,
        "kas_override": null,
        "local_conf": [],
        "machine": "qemux86-64",
        "manifest_file": null,
        "name": "",
        "no_cache": false,
        "pinned_manifest": null,
        "plan": null,
        "project": "demo/demo",
        "provisioning_time": "2023-12-09T07:57:53.449324",
        "result": "pass",
        "running_time": "2023-12-09T08:00:15.165104",
        "setup_duration": 103,
        "sources": {
            "repo": {
                "branch": "kirkstone",
                "manifest": "default.xml",
                "url": "https://gitlab.eclipse.org/eclipse/oniro-core/oniro"
            }
        },
        "state": "finished",
        "status_message": "",
        "targets": [
            "intltool-native"
        ],
        "token_name": "demo-tuxsuite",
        "uid": "2ZITcWtwDj3povtoSM0c5sk30FZ",
        "user": "demo.user@linaro.org",
        "user_agent": "tuxsuite/1.33.0",
        "waited_by": [],
        "warnings_count": 0
    }
}
```

</details>

<details>
<summary>Click to see payload sample for a plan</summary>

```json
{
    "kind": "plan",
    "status": {
        "description": "Plan Callback Tester",
        "is_public": true,
        "name": "Plan Callback Tester",
        "plan_callback": "https://tuxapi.tuxsuite.com/v1/test_callback",
        "project": "tuxsuite/demo",
        "provisioning_time": "2023-12-09T07:48:26.003703",
        "state": "finished",
        "token_name": "demo-tuxsuite",
        "uid": "2ZISTKlXYwYx1k5K4p8HIEKu7kn",
        "user": "demo.user@linaro.org",
        "user_agent": "tuxsuite/1.33.0"
    }
}
```

</details>

__NOTE__: The Tux backends use ECDSA based cryptogrphic key pairs in order to
create the signature.
