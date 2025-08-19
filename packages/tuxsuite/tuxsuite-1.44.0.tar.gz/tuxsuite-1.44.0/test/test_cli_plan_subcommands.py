# -*- coding: utf-8 -*-

import sys
import json
import pytest
import tuxsuite
import yaml


@pytest.fixture
def plan_json():
    plan = {
        "project": "tuxsuite/senthil",
        "uid": "1qsx3P3UROY9DwTUV48cEre3UO7",
        "name": "i386 kernel",
        "description": "Build and test i386 with every toolchains",
        "user": None,
        "user_agent": None,
        "provisioning_time": "2021-11-01T19:38:31.142790",
        "builds": {
            "count": 8,
            "results": [
                # Watch the error counts and warning counts which differ in
                # each build / test.
                {
                    "project": "tuxsuite/senthil",
                    "uid": "1qsx3vvpbsyQS7gVwfdwBHZzcCX",
                    "plan": "1qsx3P3UROY9DwTUV48cEre3UO7",
                    "kconfig": ["defconfig"],
                    "target_arch": "x86_64",
                    "toolchain": "clang-nightly",
                    "build_name": "",
                    "client_token": "537c0a39-5919-48a3-96c2-31773aaae988",
                    "environment": {},
                    "make_variables": {},
                    "targets": [],
                    "git_repo": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
                    "git_ref": "master",
                    "git_sha": "454859c552da78b0f587205d308401922b56863e",
                    "download_url": "https://builds.tuxbuild.com/1qsx3vvpbsyQS7gVwfdwBHZzcCX/",
                    "kernel_image": "",
                    "user": "senthil.kumaran@linaro.org",
                    "user_agent": None,
                    "state": "provisioning",  # case: status provisioning
                    "result": "pass",
                    "waited_by": ["1qsx5iBMtsjD24OgjWW9tatj4HE"],
                    "errors_count": 0,  # case: error count 0
                    "warnings_count": 0,  # case: warning count 0
                    "kernel_patch_file": None,
                    "provisioning_time": "2021-11-01T19:38:31.161747",
                    "running_time": None,
                    "finished_time": None,
                    "git_short_log": "454859c552da (\"Merge tag 'arc-5.12-rc7'\")",
                    "kernel_image_name": "bzImage",
                    "duration": 409,
                    "build_status": "pass",
                    "tuxbuild_status": "complete",
                    "kernel_version": "5.12.0-rc6",
                    "status_message": "build completed",
                },
                {
                    "project": "tuxsuite/senthil",
                    "uid": "1qsx3vvpbsyQS7gVwfdwBHZzcCX",
                    "plan": "1qsx3P3UROY9DwTUV48cEre3UO7",
                    "kconfig": ["defconfig"],
                    "target_arch": "x86_64",
                    "toolchain": "clang-nightly",
                    "build_name": "",
                    "client_token": "537c0a39-5919-48a3-96c2-31773aaae988",
                    "environment": {},
                    "make_variables": {},
                    "targets": [],
                    "git_repo": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
                    "git_ref": "master",
                    "git_sha": "454859c552da78b0f587205d308401922b56863e",
                    "download_url": "https://builds.tuxbuild.com/1qsx3vvpbsyQS7gVwfdwBHZzcCX/",
                    "kernel_image": "",
                    "user": "senthil.kumaran@linaro.org",
                    "user_agent": None,
                    "state": "finished",
                    "result": "pass",
                    "waited_by": ["1qsx5iBMtsjD24OgjWW9tatj4HE"],
                    "errors_count": 0,  # case: error count 0
                    "warnings_count": 1,  # case: warning count 1
                    "kernel_patch_file": None,
                    "provisioning_time": "2021-11-01T19:38:31.161747",
                    "running_time": None,
                    "finished_time": None,
                    "git_short_log": "454859c552da (\"Merge tag 'arc-5.12-rc7'\")",
                    "kernel_image_name": "bzImage",
                    "duration": 409,
                    "build_status": "pass",
                    "tuxbuild_status": "complete",
                    "kernel_version": "5.12.0-rc6",
                    "status_message": "build completed",
                },
                {
                    "project": "tuxsuite/senthil",
                    "uid": "1qsx3vvpbsyQS7gVwfdwBHZzcCX",
                    "plan": "1qsx3P3UROY9DwTUV48cEre3UO7",
                    "kconfig": ["defconfig"],
                    "target_arch": "x86_64",
                    "toolchain": "clang-nightly",
                    "build_name": "",
                    "client_token": "537c0a39-5919-48a3-96c2-31773aaae988",
                    "environment": {},
                    "make_variables": {},
                    "targets": [],
                    "git_repo": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
                    "git_ref": "master",
                    "git_sha": "454859c552da78b0f587205d308401922b56863e",
                    "download_url": "https://builds.tuxbuild.com/1qsx3vvpbsyQS7gVwfdwBHZzcCX/",
                    "kernel_image": "",
                    "user": "senthil.kumaran@linaro.org",
                    "user_agent": None,
                    "state": "running",  # case: status running
                    "result": "pass",
                    "waited_by": ["1qsx5iBMtsjD24OgjWW9tatj4HE"],
                    "errors_count": 0,  # case: error count 0
                    "warnings_count": 2,  # case: warning count 2
                    "kernel_patch_file": None,
                    "provisioning_time": "2021-11-01T19:38:31.161747",
                    "running_time": None,
                    "finished_time": None,
                    "git_short_log": "454859c552da (\"Merge tag 'arc-5.12-rc7'\")",
                    "kernel_image_name": "bzImage",
                    "duration": 409,
                    "build_status": "pass",
                    "tuxbuild_status": "complete",
                    "kernel_version": "5.12.0-rc6",
                    "status_message": "build completed",
                },
                {
                    "project": "tuxsuite/senthil",
                    "uid": "1qsx3vvpbsyQS7gVwfdwBHZzcCX",
                    "plan": "1qsx3P3UROY9DwTUV48cEre3UO7",
                    "kconfig": ["defconfig"],
                    "target_arch": "x86_64",
                    "toolchain": "clang-nightly",
                    "build_name": "",
                    "client_token": "537c0a39-5919-48a3-96c2-31773aaae988",
                    "environment": {},
                    "make_variables": {},
                    "targets": [],
                    "git_repo": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
                    "git_ref": "master",
                    "git_sha": "454859c552da78b0f587205d308401922b56863e",
                    "download_url": "https://builds.tuxbuild.com/1qsx3vvpbsyQS7gVwfdwBHZzcCX/",
                    "kernel_image": "",
                    "user": "senthil.kumaran@linaro.org",
                    "user_agent": None,
                    "state": "finished",
                    "result": "fail",  # case: result fail with errors/warnings
                    "waited_by": ["1qsx5iBMtsjD24OgjWW9tatj4HE"],
                    "errors_count": 2,
                    "warnings_count": 4,
                    "kernel_patch_file": None,
                    "provisioning_time": "2021-11-01T19:38:31.161747",
                    "running_time": None,
                    "finished_time": None,
                    "git_short_log": "454859c552da (\"Merge tag 'arc-5.12-rc7'\")",
                    "kernel_image_name": "bzImage",
                    "duration": 409,
                    "build_status": "fail",
                    "tuxbuild_status": "complete",
                    "kernel_version": "5.12.0-rc6",
                    "status_message": "build completed",
                },
                {
                    "project": "tuxsuite/senthil",
                    "uid": "1qsx3vvpbsyQS7gVwfdwBHZzcCX",
                    "plan": "1qsx3P3UROY9DwTUV48cEre3UO7",
                    "kconfig": ["defconfig"],
                    "target_arch": "x86_64",
                    "toolchain": "clang-nightly",
                    "build_name": "",
                    "client_token": "537c0a39-5919-48a3-96c2-31773aaae988",
                    "environment": {},
                    "make_variables": {},
                    "targets": [],
                    "git_repo": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
                    "git_ref": "master",
                    "git_sha": "454859c552da78b0f587205d308401922b56863e",
                    "download_url": "https://builds.tuxbuild.com/1qsx3vvpbsyQS7gVwfdwBHZzcCX/",
                    "kernel_image": "",
                    "user": "senthil.kumaran@linaro.org",
                    "user_agent": None,
                    "state": "finished",
                    "result": "fail",  # case: result fail with 1 error
                    "waited_by": ["1qsx5iBMtsjD24OgjWW9tatj4HE"],
                    "errors_count": 1,
                    "warnings_count": 4,
                    "kernel_patch_file": None,
                    "provisioning_time": "2021-11-01T19:38:31.161747",
                    "running_time": None,
                    "finished_time": None,
                    "git_short_log": "454859c552da (\"Merge tag 'arc-5.12-rc7'\")",
                    "kernel_image_name": "bzImage",
                    "duration": 409,
                    "build_status": "fail",
                    "tuxbuild_status": "complete",
                    "kernel_version": "5.12.0-rc6",
                    "status_message": "build completed",
                },
                {
                    "project": "tuxsuite/senthil",
                    "uid": "1qsx3vvpbsyQS7gVwfdwBHZzcCX",
                    "plan": "1qsx3P3UROY9DwTUV48cEre3UO7",
                    "kconfig": ["defconfig"],
                    "target_arch": "x86_64",
                    "toolchain": "clang-nightly",
                    "build_name": "",
                    "client_token": "537c0a39-5919-48a3-96c2-31773aaae988",
                    "environment": {},
                    "make_variables": {},
                    "targets": [],
                    "git_repo": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
                    "git_ref": "master",
                    "git_sha": "454859c552da78b0f587205d308401922b56863e",
                    "download_url": "https://builds.tuxbuild.com/1qsx3vvpbsyQS7gVwfdwBHZzcCX/",
                    "kernel_image": "",
                    "user": "senthil.kumaran@linaro.org",
                    "user_agent": None,
                    "state": "finished",
                    "result": "error",  # case: result error with 1 error
                    "waited_by": ["1qsx5iBMtsjD24OgjWW9tatj4HE"],
                    "errors_count": 1,
                    "warnings_count": 4,
                    "kernel_patch_file": None,
                    "provisioning_time": "2021-11-01T19:38:31.161747",
                    "running_time": None,
                    "finished_time": None,
                    "git_short_log": "454859c552da (\"Merge tag 'arc-5.12-rc7'\")",
                    "kernel_image_name": "bzImage",
                    "duration": 409,
                    "build_status": "error",
                    "tuxbuild_status": "complete",
                    "kernel_version": "5.12.0-rc6",
                    "status_message": "build completed",
                },
                {
                    "project": "tuxsuite/senthil",
                    "uid": "1qsx3vvpbsyQS7gVwfdwBHZzcCY",
                    "plan": "1qsx3P3UROY9DwTUV48cEre3UO7",
                    "kconfig": ["defconfig"],
                    "target_arch": "x86_64",
                    "toolchain": "clang-nightly",
                    "build_name": "",
                    "client_token": "537c0a39-5919-48a3-96c2-31773aaae988",
                    "environment": {},
                    "make_variables": {},
                    "targets": [],
                    "git_repo": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
                    "git_ref": "master",
                    "git_sha": "454859c552da78b0f587205d308401922b56863e",
                    "download_url": "https://builds.tuxbuild.com/1qsx3vvpbsyQS7gVwfdwBHZzcCY/",
                    "kernel_image": "",
                    "user": "senthil.kumaran@linaro.org",
                    "user_agent": None,
                    "state": "finished",
                    "result": "canceled",  # case: Plan Canceled
                    "waited_by": ["TEST#1qsx5iBMtsjD24OgjWW9tatj4HG"],
                    "errors_count": 1,
                    "warnings_count": 4,
                    "kernel_patch_file": None,
                    "provisioning_time": "2021-11-01T19:38:31.161747",
                    "running_time": None,
                    "finished_time": None,
                    "git_short_log": "454859c552da (\"Merge tag 'arc-5.12-rc7'\")",
                    "kernel_image_name": "bzImage",
                    "duration": 40,
                    "build_status": "error",
                    "tuxbuild_status": "complete",
                    "kernel_version": "5.12.0-rc6",
                    "status_message": "build canceled",
                },
                {
                    "project": "tuxsuite/senthil",
                    "uid": "1qsx3vvpbsyQS7gVwfdwBHZzcCR",
                    "plan": "1qsx3P3UROY9DwTUV48cEre3UO7",
                    "kconfig": ["defconfig"],
                    "target_arch": "x86_64",
                    "toolchain": "clang-nightly",
                    "build_name": "",
                    "client_token": "537c0a39-5919-48a3-96c2-31773aaae988",
                    "environment": {},
                    "make_variables": {},
                    "targets": [],
                    "git_repo": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
                    "git_ref": "master",
                    "git_sha": "454859c552da78b0f587205d308401922b56863e",
                    "download_url": "https://builds.tuxbuild.com/1qsx3vvpbsyQS7gVwfdwBHZzcCR/",
                    "kernel_image": "",
                    "user": "senthil.kumaran@linaro.org",
                    "user_agent": None,
                    "state": "finished",
                    "result": "unknown",  # case: result unknown
                    "waited_by": ["TEST#1qsx5iBMtsjD24OgjWW9tatj4HF"],
                    "errors_count": 1,
                    "warnings_count": 4,
                    "kernel_patch_file": None,
                    "provisioning_time": "2021-11-01T19:38:31.161747",
                    "running_time": None,
                    "finished_time": None,
                    "git_short_log": "454859c552da (\"Merge tag 'arc-5.12-rc7'\")",
                    "kernel_image_name": "bzImage",
                    "duration": 40,
                    "build_status": "error",
                    "tuxbuild_status": "complete",
                    "kernel_version": "5.12.0-rc6",
                    "status_message": "build running",
                },
                {
                    "project": "tuxsuite/senthil",
                    "uid": "2Y9ohCShBkC5TOD8ZWjYnVkKXLL",
                    "plan": "1qsx3P3UROY9DwTUV48cEre3UO7",
                    "kconfig": ["defconfig"],
                    "target_arch": "x86_64",
                    "toolchain": "clang-nightly",
                    "build_name": "",
                    "client_token": "537c0a39-5919-48a3-96c2-31773aaae988",
                    "environment": {},
                    "make_variables": {},
                    "targets": [],
                    "git_repo": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
                    "git_ref": "master",
                    "git_sha": "454859c552da78b0f587205d308401922b56863e",
                    "download_url": "https://builds.tuxbuild.com/1qsx3vvpbsyQS7gVwfdwBHZzcCX/",
                    "kernel_image": "",
                    "user": "senthil.kumaran@linaro.org",
                    "user_agent": None,
                    "state": "finished",
                    "result": "pass",
                    "waited_by": [
                        "TEST#2Y9ohLIszmyc2AUIODdqrCaptFm"
                    ],  # case: sanity dependency
                    "errors_count": 0,
                    "warnings_count": 1,
                    "kernel_patch_file": None,
                    "provisioning_time": "2021-11-01T19:38:31.161747",
                    "running_time": None,
                    "finished_time": None,
                    "git_short_log": "454859c552da (\"Merge tag 'arc-5.12-rc7'\")",
                    "kernel_image_name": "bzImage",
                    "duration": 409,
                    "build_status": "pass",
                    "tuxbuild_status": "complete",
                    "kernel_version": "5.12.0-rc6",
                    "status_message": "build completed",
                },
            ],
            "next": None,
        },
        "tests": {
            "count": 8,
            "results": [
                {
                    "project": "tuxsuite/senthil",
                    "device": "qemu-x86_64",
                    "uid": "1qsx5iBMtsjD24OgjWW9tatj4HE",
                    "kernel": "https://builds.tuxbuild.com/1qsx3vvpbsyQS7gVwfdwBHZzcCX/bzImage",
                    "ap_romfw": None,
                    "mcp_fw": None,
                    "mcp_romfw": None,
                    "modules": None,
                    "parameters": None,
                    "rootfs": None,
                    "scp_fw": None,
                    "scp_romfw": None,
                    "fip": None,
                    "tests": ["boot", "ltp-smoke"],
                    "user": None,
                    "user_agent": None,
                    "state": "waiting",  # case: status waiting
                    "result": "pass",  # case: result pass
                    "results": {"boot": "pass", "ltp-smoke": "pass"},
                    "plan": "1qsx3P3UROY9DwTUV48cEre3UO7",
                    "download_url": "https://storage.tuxsuite.com/uid1/",
                    "waiting_for": "BUILD#1qsx3vvpbsyQS7gVwfdwBHZzcCX",
                    "boot_args": None,
                    "provisioning_time": "2021-04-08T11:46:53.297621",
                    "running_time": "2021-04-08T11:46:54.355808",
                    "finished_time": "2021-04-08T11:47:39.082080",
                    "duration": 45,
                    "test_name": "",
                },
                {
                    "project": "tuxsuite/senthil",
                    "device": "qemu-x86_64",
                    "uid": "1qsx5iBMtsjD24OgjWW9tatj4HE",
                    "kernel": "https://builds.tuxbuild.com/1qsx3vvpbsyQS7gVwfdwBHZzcCX/bzImage",
                    "ap_romfw": None,
                    "mcp_fw": None,
                    "mcp_romfw": None,
                    "modules": None,
                    "parameters": None,
                    "rootfs": None,
                    "scp_fw": None,
                    "scp_romfw": None,
                    "fip": None,
                    "tests": ["boot", "ltp-smoke"],
                    "user": None,
                    "user_agent": None,
                    "state": "provisioning",  # case: status provisioning
                    "result": "fail",  # case: result fail
                    "results": {"boot": "fail", "ltp-smoke": "pass"},
                    "plan": "1qsx3P3UROY9DwTUV48cEre3UO7",
                    "download_url": "https://storage.tuxsuite.com/uid2/",
                    "waiting_for": "BUILD#1qsx3vvpbsyQS7gVwfdwBHZzcCX",
                    "boot_args": None,
                    "provisioning_time": "2021-04-08T11:46:53.297621",
                    "running_time": "2021-04-08T11:46:54.355808",
                    "finished_time": "2021-04-08T11:47:39.082080",
                    "duration": 45,
                    "test_name": "",
                },
                {
                    "project": "tuxsuite/senthil",
                    "device": "qemu-x86_64",
                    "uid": "1qsx5iBMtsjD24OgjWW9tatj4HG",
                    "kernel": "https://builds.tuxbuild.com/1qsx3vvpbsyQS7gVwfdwBHZzcCY/bzImage",
                    "ap_romfw": None,
                    "mcp_fw": None,
                    "mcp_romfw": None,
                    "modules": None,
                    "parameters": None,
                    "rootfs": None,
                    "scp_fw": None,
                    "scp_romfw": None,
                    "fip": None,
                    "tests": ["boot", "ltp-smoke"],
                    "user": None,
                    "user_agent": None,
                    "state": "finished",  # case: status finished
                    "result": "canceled",  # case: result canceled
                    "results": {"boot": "unknown", "ltp-smoke": "canceled"},
                    "plan": "1qsx3P3UROY9DwTUV48cEre3UO7",
                    "download_url": "https://storage.tuxsuite.com/uid3/",
                    "waiting_for": "BUILD#1qsx3vvpbsyQS7gVwfdwBHZzcCY",
                    "boot_args": None,
                    "provisioning_time": "2021-04-08T11:46:53.297621",
                    "running_time": "2021-04-08T11:46:54.355808",
                    "finished_time": "2021-04-08T11:47:39.082080",
                    "duration": 45,
                    "test_name": "",
                },
                {
                    "project": "tuxsuite/senthil",
                    "device": "qemu-x86_64",
                    "uid": "1qsx5iBMtsjD24OgjWW9tatj4HF",
                    "kernel": "https://builds.tuxbuild.com/1qsx3vvpbsyQS7gVwfdwBHZzcCR/bzImage",
                    "ap_romfw": None,
                    "mcp_fw": None,
                    "mcp_romfw": None,
                    "modules": None,
                    "parameters": None,
                    "rootfs": None,
                    "scp_fw": None,
                    "scp_romfw": None,
                    "fip": None,
                    "tests": ["boot", "ltp-smoke"],
                    "user": None,
                    "user_agent": None,
                    "state": "finished",  # case: status running
                    "result": "unknown",  # case: result unknown
                    "results": {"boot": "fail", "ltp-smoke": "pass"},
                    "plan": "1qsx3P3UROY9DwTUV48cEre3UO7",
                    "download_url": "https://storage.tuxsuite.com/uid4/",
                    "waiting_for": "BUILD#1qsx3vvpbsyQS7gVwfdwBHZzcCR",
                    "boot_args": None,
                    "provisioning_time": "2021-04-08T11:46:53.297621",
                    "running_time": "2021-04-08T11:46:54.355808",
                    "finished_time": "2021-04-08T11:47:39.082080",
                    "duration": 45,
                    "test_name": "",
                },
                {
                    "project": "tuxsuite/senthil",
                    "device": "qemu-x86_64",
                    "uid": "1qsx5iBMtsjD24OgjWW9tatj4HE",
                    "kernel": "https://builds.tuxbuild.com/1qsx3vvpbsyQS7gVwfdwBHZzcCX/bzImage",
                    "ap_romfw": None,
                    "mcp_fw": None,
                    "mcp_romfw": None,
                    "modules": None,
                    "parameters": None,
                    "rootfs": None,
                    "scp_fw": None,
                    "scp_romfw": None,
                    "fip": None,
                    "tests": ["boot", "ltp-smoke"],
                    "user": None,
                    "user_agent": None,
                    "state": "running",  # case: status running
                    "result": "error",  # case: result error
                    "results": {"boot": "fail", "ltp-smoke": "pass"},
                    "plan": "1qsx3P3UROY9DwTUV48cEre3UO7",
                    "download_url": "https://storage.tuxsuite.com/uid5/",
                    "waiting_for": "BUILD#1qsx3vvpbsyQS7gVwfdwBHZzcCX",
                    "boot_args": None,
                    "provisioning_time": "2021-04-08T11:46:53.297621",
                    "running_time": "2021-04-08T11:46:54.355808",
                    "finished_time": "2021-04-08T11:47:39.082080",
                    "duration": 45,
                    "test_name": "",
                },
                {
                    "project": "tuxsuite/senthil",
                    "device": "qemu-x86_64",
                    "uid": "1qsx5iBMtsjD24OgjWW9tatj4HE",
                    "kernel": "https://builds.tuxbuild.com/1qsx3vvpbsyQS7gVwfdwBHZzcCX/bzImage",
                    "ap_romfw": None,
                    "mcp_fw": None,
                    "mcp_romfw": None,
                    "modules": None,
                    "parameters": None,
                    "rootfs": None,
                    "scp_fw": None,
                    "scp_romfw": None,
                    "fip": None,
                    "tests": ["boot", "ltp-smoke"],
                    "user": None,
                    "user_agent": None,
                    "state": "finished",
                    "result": "pass",  # case: result pass
                    "results": {"boot": "pass", "ltp-smoke": "pass"},
                    "plan": "BUILD#1qsx3P3UROY9DwTUV48cEre3UO7",
                    "download_url": "https://storage.tuxsuite.com/uid6/",
                    "waiting_for": None,  # case: standalone test
                    "boot_args": None,
                    "provisioning_time": "2021-04-08T11:46:53.297621",
                    "running_time": "2021-04-08T11:46:54.355808",
                    "finished_time": "2021-04-08T11:47:39.082080",
                    "duration": 45,
                    "test_name": "",
                },
                {
                    "project": "tuxsuite/senthil",
                    "device": "qemu-x86_64",
                    "uid": "1qsx5iBMtsjD24OgjWW9tatj4HE",
                    "kernel": "https://builds.tuxbuild.com/1qsx3vvpbsyQS7gVwfdwBHZzcCX/bzImage",
                    "ap_romfw": None,
                    "mcp_fw": None,
                    "mcp_romfw": None,
                    "modules": None,
                    "parameters": None,
                    "rootfs": None,
                    "scp_fw": None,
                    "scp_romfw": None,
                    "fip": None,
                    "tests": ["boot", "ltp-smoke"],
                    "user": None,
                    "user_agent": None,
                    "state": "finished",
                    "result": "fail",  # case: result fail
                    "results": {"boot": "unknown", "ltp-smoke": "pass"},
                    "plan": "1qsx3P3UROY9DwTUV48cEre3UO7",
                    "download_url": "https://storage.tuxsuite.com/uid7/",
                    "waiting_for": None,  # case: standalone test
                    "boot_args": None,
                    "provisioning_time": "2021-04-08T11:46:53.297621",
                    "running_time": "2021-04-08T11:46:54.355808",
                    "finished_time": "2021-04-08T11:47:39.082080",
                    "duration": 45,
                    "test_name": "",
                },
                {
                    "project": "tuxsuite/senthil",
                    "device": "qemu-x86_64",
                    "uid": "1qsx5iBMtsjD24OgjWW9tatj4HE",
                    "kernel": "https://builds.tuxbuild.com/1qsx3vvpbsyQS7gVwfdwBHZzcCX/bzImage",
                    "ap_romfw": None,
                    "mcp_fw": None,
                    "mcp_romfw": None,
                    "modules": None,
                    "parameters": None,
                    "rootfs": None,
                    "scp_fw": None,
                    "scp_romfw": None,
                    "fip": None,
                    "tests": ["boot", "ltp-smoke"],
                    "user": None,
                    "user_agent": None,
                    "state": "finished",
                    "result": "canceled",  # case: result error
                    "results": {"boot": "fail", "ltp-smoke": "pass"},
                    "plan": "1qsx3P3UROY9DwTUV48cEre3UO7",
                    "download_url": "https://storage.tuxsuite.com/uid8/",
                    "waiting_for": None,  # case: standalone test
                    "boot_args": None,
                    "provisioning_time": "2021-04-08T11:46:53.297621",
                    "running_time": "2021-04-08T11:46:54.355808",
                    "finished_time": "2021-04-08T11:47:39.082080",
                    "duration": 45,
                    "test_name": "",
                },
                {
                    "project": "tuxsuite/senthil",
                    "device": "qemu-x86_64",
                    "uid": "2Y9ohNoD4ax3nYiZejUYhT0sIeb",
                    "kernel": "https://builds.tuxbuild.com/1qsx3vvpbsyQS7gVwfdwBHZzcCX/bzImage",
                    "ap_romfw": None,
                    "mcp_fw": None,
                    "mcp_romfw": None,
                    "modules": None,
                    "parameters": None,
                    "rootfs": None,
                    "scp_fw": None,
                    "scp_romfw": None,
                    "fip": None,
                    "tests": ["boot", "ltp-smoke"],
                    "user": None,
                    "user_agent": None,
                    "state": "finished",
                    "result": "pass",
                    "results": {"boot": "pass", "ltp-smoke": "pass"},
                    "plan": "1qsx3P3UROY9DwTUV48cEre3UO7",
                    "download_url": "https://storage.tuxsuite.com/uid9/",
                    "waiting_for": "TEST#2Y9ohLIszmyc2AUIODdqrCaptFm",
                    "boot_args": None,
                    "provisioning_time": "2021-04-08T11:46:53.297621",
                    "running_time": "2021-04-08T11:46:54.355808",
                    "finished_time": "2021-04-08T11:47:39.082080",
                    "duration": 45,
                    "test_name": "",
                },
                {
                    "project": "tuxsuite/senthil",
                    "device": "qemu-x86_64",
                    "uid": "2Y9ohLIszmyc2AUIODdqrCaptFm",
                    "kernel": "https://builds.tuxbuild.com/1qsx3vvpbsyQS7gVwfdwBHZzcCX/bzImage",
                    "ap_romfw": None,
                    "mcp_fw": None,
                    "mcp_romfw": None,
                    "modules": None,
                    "parameters": None,
                    "rootfs": None,
                    "scp_fw": None,
                    "scp_romfw": None,
                    "fip": None,
                    "tests": ["boot", "ltp-smoke"],
                    "user": None,
                    "user_agent": None,
                    "state": "finished",
                    "result": "pass",  # case: result pass
                    "results": {"boot": "pass", "ltp-smoke": "pass"},
                    "plan": "1qsx3P3UROY9DwTUV48cEre3UO7",
                    "download_url": "https://storage.tuxsuite.com/uid10/",
                    "waiting_for": "BUILD#2Y9ohCShBkC5TOD8ZWjYnVkKXLL",
                    "waited_by": [
                        "TEST#2Y9ohNoD4ax3nYiZejUYhT0sIeb"
                    ],  # case: sanity test
                    "boot_args": None,
                    "provisioning_time": "2021-04-08T11:46:53.297621",
                    "running_time": "2021-04-08T11:46:54.355808",
                    "finished_time": "2021-04-08T11:47:39.082080",
                    "duration": 45,
                    "test_name": "",
                },
            ],
            "next": None,
        },
        "oebuilds": {"count": 0, "results": [], "next": None},
    }
    return json.dumps(plan).encode("utf-8")


@pytest.fixture
def bake_plan_json():
    bake_plan = {
        "project": "tuxsuite/alok",
        "uid": "29EbSmPfjpbYQj8ZuaBpsiA8CbW",
        "name": "armv7 validation",
        "description": "Build and test linux kernel for armv7",
        "user": "alok.ranjan@linaro.org",
        "user_agent": "tuxsuite/0.43.10",
        "provisioning_time": "2022-05-16T06:06:33.830964",
        "oebuilds": {
            "count": 4,
            "results": [
                {
                    "project": "tuxsuite/alok",
                    "uid": "29EbSyjM7FZgX1X2FDvpq0hxomz",
                    "plan": "29EbSmPfjpbYQj8ZuaBpsiA8CbW",
                    "distro": "rpb",
                    "machine": "ledge-multi-armv7",
                    "container": "ubuntu-20.04",
                    "environment": {},
                    "local_conf": [],
                    "bblayers_conf": [],
                    "artifacts": [],
                    "target": "rpb-console-image rpb-console-image-test rpb-desktop-image rpb-desktop-image-test",
                    "envsetup": "setup-environment",
                    "user": "alok.ranjan@linaro.org",
                    "user_agent": "tuxsuite/0.43.10",
                    "download_url": "https://oebuilds.tuxbuild.com/29EbSyjM7FZgX1X2FDvpq0hxomz/",
                    "sources": {
                        "repo": {
                            "branch": "qcom/dunfell",
                            "manifest": "default.xml",
                            "url": "https://github.com/96boards/oe-rpb-manifest.git",
                        }
                    },
                    "state": "finished",
                    "result": "fail",
                    "waited_by": [],
                    "errors_count": 0,
                    "warnings_count": 0,
                    "running_time": "2022-05-16T06:09:04.713320",
                    "finished_time": "2022-05-16T06:09:46.534596",
                    "manifest_file": "None",
                    "provisioning_time": "2022-05-16T06:06:35.312535",
                    "duration": 43,
                    "status_message": "",
                },
                {
                    "project": "tuxsuite/alok",
                    "uid": "29EbSycpmLu8Nut5SoZFCwJaRER",
                    "plan": "29EbSmPfjpbYQj8ZuaBpsiA8CbW",
                    "distro": "rpb",
                    "machine": "dragonboard-845c",
                    "container": "ubuntu-20.04",
                    "environment": {},
                    "local_conf": [],
                    "bblayers_conf": [],
                    "artifacts": [],
                    "target": "rpb-console-image rpb-console-image-test rpb-desktop-image rpb-desktop-image-test",
                    "envsetup": "setup-environment",
                    "user": "alok.ranjan@linaro.org",
                    "user_agent": "tuxsuite/0.43.10",
                    "download_url": "https://oebuilds.tuxbuild.com/29EbSycpmLu8Nut5SoZFCwJaRER/",
                    "sources": {
                        "repo": {
                            "branch": "qcom/dunfell",
                            "manifest": "default.xml",
                            "url": "https://github.com/96boards/oe-rpb-manifest.git",
                        }
                    },
                    "state": "finished",
                    "result": "pass",
                    "waited_by": [],
                    "errors_count": 0,
                    "warnings_count": 0,
                    "running_time": "2022-05-16T06:09:04.709211",
                    "finished_time": "2022-05-16T08:06:04.740891",
                    "manifest_file": "None",
                    "provisioning_time": "2022-05-16T06:06:35.312683",
                    "duration": 7021,
                    "status_message": "",
                },
                {
                    "project": "tuxsuite/alok",
                    "uid": "29EbSyjM7FZgX1X2FDvpq0hxomR",
                    "plan": "29EbSmPfjpbYQj8ZuaBpsiA8CbW",
                    "distro": "rpb",
                    "machine": "ledge-multi-armv7",
                    "container": "ubuntu-20.04",
                    "environment": {},
                    "local_conf": [],
                    "bblayers_conf": [],
                    "artifacts": [],
                    "target": "rpb-console-image rpb-console-image-test rpb-desktop-image rpb-desktop-image-test",
                    "envsetup": "setup-environment",
                    "user": "alok.ranjan@linaro.org",
                    "user_agent": "tuxsuite/0.43.10",
                    "download_url": "https://oebuilds.tuxbuild.com/29EbSyjM7FZgX1X2FDvpq0hxomR/",
                    "sources": {
                        "repo": {
                            "branch": "qcom/dunfell",
                            "manifest": "default.xml",
                            "url": "https://github.com/96boards/oe-rpb-manifest.git",
                        }
                    },
                    "state": "finished",
                    "result": "canceled",  # case canceled oebuild
                    "waited_by": [],
                    "errors_count": 0,
                    "warnings_count": 0,
                    "running_time": "2022-05-16T06:09:04.713320",
                    "finished_time": "2022-05-16T06:09:46.534596",
                    "manifest_file": "None",
                    "provisioning_time": "2022-05-16T06:06:35.312535",
                    "duration": 45,
                    "status_message": "oebuild canceled",
                },
                {
                    "project": "tuxsuite/alok",
                    "uid": "29EbSyjM7FZgX1X2FDvpq0hxomF",
                    "plan": "29EbSmPfjpbYQj8ZuaBpsiA8CbW",
                    "distro": "rpb",
                    "machine": "ledge-multi-armv7",
                    "container": "ubuntu-20.04",
                    "environment": {},
                    "local_conf": [],
                    "bblayers_conf": [],
                    "artifacts": [],
                    "target": "rpb-console-image rpb-console-image-test rpb-desktop-image rpb-desktop-image-test",
                    "envsetup": "setup-environment",
                    "user": "alok.ranjan@linaro.org",
                    "user_agent": "tuxsuite/0.43.10",
                    "download_url": "https://oebuilds.tuxbuild.com/29EbSyjM7FZgX1X2FDvpq0hxomF/",
                    "sources": {
                        "repo": {
                            "branch": "qcom/dunfell",
                            "manifest": "default.xml",
                            "url": "https://github.com/96boards/oe-rpb-manifest.git",
                        }
                    },
                    "state": "finished",
                    "result": "unknown",  # case unknown oebuild
                    "waited_by": [],
                    "errors_count": 0,
                    "warnings_count": 0,
                    "running_time": "2022-05-16T06:09:04.713320",
                    "finished_time": "2022-05-16T06:09:46.534596",
                    "manifest_file": "None",
                    "provisioning_time": "2022-05-16T06:06:35.312535",
                    "duration": 45,
                    "status_message": "oebuild still unknown",
                },
            ],
            "next": None,
        },
        "builds": {"count": 0, "results": [], "next": None},
        "tests": {"count": 0, "results": [], "next": None},
    }
    return json.dumps(bake_plan).encode("utf-8")


@pytest.fixture
def plan_list_json():
    plan_list = {
        "count": 1,
        "results": [
            {
                "project": "tuxsuite/senthil",
                "uid": "1zjHLXHufFpOd5XjuhkWpYZfK0y",
                "name": "linux stable",
                "description": "Build linux stable",
                "user": "senthil.kumaran@linaro.org",
                "user_agent": "tuxsuite/0.35.0",
                "provisioning_time": "2021-10-19T14:42:01.896219",
            },
        ],
        "next": None,
    }
    return json.dumps(plan_list).encode("utf-8")


def test_plan_handle_get(mocker, plan_json, config, response, monkeypatch, tmp_path):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "plan", "get", "1tOhlD2nkPsRNNTMB5Lj09n1IVQ"]
    )
    response.status_code = 200
    response._content = plan_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1

    # Test --json
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "plan", "get", "1tOhlD2nkPsRNNTMB5Lj09n1IVQ", "--json"],
    )
    response.status_code = 200
    response._content = plan_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1

    # Test --json-out
    json_path = f"{tmp_path}/plan.json"
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "plan",
            "get",
            "1tOhlD2nkPsRNNTMB5Lj09n1IVQ",
            "--json-out",
            json_path,
        ],
    )
    response.status_code = 200
    response._content = plan_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1
    assert len(json.load(open(json_path, "r"))) > 0

    # Test failure case when the response is not 200
    response.status_code = 500
    get_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(NotImplementedError):
        tuxsuite.cli.main()
    assert get_req.call_count == 1

    mocker.resetall()
    response.status_code = 200
    response._content = plan_json
    get_req = mocker.patch("requests.get", return_value=response)
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "plan", "get", "1tOhlD2nkPsRNNTMB5Lj09n1IVQ", "--json"],
    )
    tuxsuite.cli.main()

    # Test failure case when the response is 404
    response.status_code = 404
    get_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(SystemExit) as exit:
        tuxsuite.cli.main()
    assert exit.value.code == 1


def test_plan_handle_wait(mocker, plan_json, config, response, monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "plan", "wait", "1tOhlD2nkPsRNNTMB5Lj09n1IVQ"]
    )
    response.status_code = 200
    response._content = plan_json
    wait_req = mocker.patch("requests.get", return_value=response)
    mocker.patch("tuxsuite.build.get_request", return_value=response)
    mocked_plan_get = mocker.patch(
        "tuxsuite.Plan.get_plan",
        return_value={
            "builds": {
                "1qsx3vvpbsyQS7gVwfdwBHZzcCY": {
                    "project": "tuxsuite/senthil",
                    "uid": "1qsx3vvpbsyQS7gVwfdwBHZzcCY",
                    "plan": "1qsx3P3UROY9DwTUV48cEre3UO7",
                    "kconfig": ["defconfig"],
                    "target_arch": "x86_64",
                    "toolchain": "clang-nightly",
                    "build_name": "",
                    "client_token": "537c0a39-5919-48a3-96c2-31773aaae988",
                    "environment": {},
                    "make_variables": {},
                    "targets": [],
                    "git_repo": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
                    "git_ref": "master",
                    "git_sha": "454859c552da78b0f587205d308401922b56863e",
                    "download_url": "https://builds.tuxbuild.com/1qsx3vvpbsyQS7gVwfdwBHZzcCY/",
                    "kernel_image": "",
                    "user": "senthil.kumaran@linaro.org",
                    "user_agent": None,
                    "state": "finished",
                    "result": "canceled",  # case: Plan Canceled
                    "waited_by": ["TEST#1qsx5iBMtsjD24OgjWW9tatj4HG"],
                    "errors_count": 1,
                    "warnings_count": 4,
                    "kernel_patch_file": None,
                    "provisioning_time": "2021-11-01T19:38:31.161747",
                    "running_time": None,
                    "finished_time": None,
                    "git_short_log": "454859c552da (\"Merge tag 'arc-5.12-rc7'\")",
                    "kernel_image_name": "bzImage",
                    "duration": 40,
                    "build_status": "error",
                    "tuxbuild_status": "complete",
                    "kernel_version": "5.12.0-rc6",
                    "status_message": "build canceled",
                },
                "1qsx3vvpbsyQS7gVwfdwBHZzcCR": {
                    "project": "tuxsuite/senthil",
                    "uid": "1qsx3vvpbsyQS7gVwfdwBHZzcCR",
                    "plan": "1qsx3P3UROY9DwTUV48cEre3UO7",
                    "kconfig": ["defconfig"],
                    "target_arch": "x86_64",
                    "toolchain": "clang-nightly",
                    "build_name": "",
                    "client_token": "537c0a39-5919-48a3-96c2-31773aaae988",
                    "environment": {},
                    "make_variables": {},
                    "targets": [],
                    "git_repo": "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git",
                    "git_ref": "master",
                    "git_sha": "454859c552da78b0f587205d308401922b56863e",
                    "download_url": "https://builds.tuxbuild.com/1qsx3vvpbsyQS7gVwfdwBHZzcCR/",
                    "kernel_image": "",
                    "user": "senthil.kumaran@linaro.org",
                    "user_agent": None,
                    "state": "finished",
                    "result": "unknown",  # case: result unknown
                    "waited_by": ["TEST#1qsx5iBMtsjD24OgjWW9tatj4HF"],
                    "errors_count": 1,
                    "warnings_count": 4,
                    "kernel_patch_file": None,
                    "provisioning_time": "2021-11-01T19:38:31.161747",
                    "running_time": None,
                    "finished_time": None,
                    "git_short_log": "454859c552da (\"Merge tag 'arc-5.12-rc7'\")",
                    "kernel_image_name": "bzImage",
                    "duration": 40,
                    "build_status": "error",
                    "tuxbuild_status": "complete",
                    "kernel_version": "5.12.0-rc6",
                    "status_message": "build running",
                },
            },
            "tests": {
                "1qsx5iBMtsjD24OgjWW9tatj4HE": {
                    "project": "tuxsuite/senthil",
                    "device": "qemu-x86_64",
                    "uid": "1qsx5iBMtsjD24OgjWW9tatj4HE",
                    "kernel": "https://builds.tuxbuild.com/1qsx3vvpbsyQS7gVwfdwBHZzcCX/bzImage",
                    "ap_romfw": None,
                    "mcp_fw": None,
                    "mcp_romfw": None,
                    "modules": None,
                    "parameters": None,
                    "rootfs": None,
                    "scp_fw": None,
                    "scp_romfw": None,
                    "fip": None,
                    "tests": ["boot", "ltp-smoke"],
                    "user": None,
                    "user_agent": None,
                    "state": "finished",
                    "result": "pass",  # case: result pass
                    "results": {"boot": "pass", "ltp-smoke": "pass"},
                    "plan": "1qsx3P3UROY9DwTUV48cEre3UO7",
                    "waiting_for": "BUILD#1qsx3vvpbsyQS7gVwfdwBHZzcCX",
                    "boot_args": None,
                    "provisioning_time": "2021-04-08T11:46:53.297621",
                    "running_time": "2021-04-08T11:46:54.355808",
                    "finished_time": "2021-04-08T11:47:39.082080",
                    "duration": 45,
                },
                "2qsx5iBMtsjD24OgjWW9tatj4HE": {
                    "project": "tuxsuite/senthil",
                    "device": "qemu-x86_64",
                    "uid": "2qsx5iBMtsjD24OgjWW9tatj4HE",
                    "kernel": "https://builds.tuxbuild.com/1qsx3vvpbsyQS7gVwfdwBHZzcCX/bzImage",
                    "ap_romfw": None,
                    "mcp_fw": None,
                    "mcp_romfw": None,
                    "modules": None,
                    "parameters": None,
                    "rootfs": None,
                    "scp_fw": None,
                    "scp_romfw": None,
                    "fip": None,
                    "tests": ["boot", "ltp-smoke"],
                    "user": None,
                    "user_agent": None,
                    "state": "finished",
                    "result": "fail",  # case: result fail
                    "results": {"boot": "fail", "ltp-smoke": "pass"},
                    "plan": "1qsx3P3UROY9DwTUV48cEre3UO7",
                    "waiting_for": "BUILD#1qsx3vvpbsyQS7gVwfdwBHZzcCX",
                    "boot_args": None,
                    "provisioning_time": "2021-04-08T11:46:53.297621",
                    "running_time": "2021-04-08T11:46:54.355808",
                    "finished_time": "2021-04-08T11:47:39.082080",
                    "duration": 45,
                },
            },
        },
    )

    tuxsuite.cli.main()
    mocked_plan_get.assert_called()
    assert wait_req.call_count == 1

    # Test failure case when the response is not 200
    response.status_code = 500
    wait_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(NotImplementedError):
        tuxsuite.cli.main()
    assert wait_req.call_count == 1


def test_plan_handle_cancel(mocker, plan_json, config, response, monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "plan", "cancel", "1tOhlD2nkPsRNNTMB5Lj09n1IVQ"]
    )
    response.status_code = 200
    response._content = plan_json
    post_req = mocker.patch("requests.post", return_value=response)
    response.status_code = 404
    response._content = plan_json
    mocker.patch("requests.get", return_value=response)
    with pytest.raises(SystemExit):
        tuxsuite.cli.main()
    response.status_code = 200
    response._content = plan_json
    mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    post_req.assert_called_with(
        "https://tuxapi.tuxsuite.com/v1/groups/tuxsuite/projects/tux/plans/1tOhlD2nkPsRNNTMB5Lj09n1IVQ/cancel",
        headers={
            "User-Agent": "tuxsuite.cli/0.1",
            "Authorization": "Q9qMlmkjkIuIGmEAw-Mf53i_qoJ8Z2eGYCmrNx16ZLLQGrXAHRiN2ce5DGlAebOmnJFp9Ggcq9l6quZdDTtrkw",
        },
        json={},
    )
    assert post_req.call_count == 1

    # Test failure case when the response is not 200
    response.status_code = 500
    post_req = mocker.patch("requests.post", return_value=response)
    with pytest.raises(tuxsuite.exceptions.URLNotFound):
        tuxsuite.cli.main()
    assert post_req.call_count == 1


def test_plan_handle_list(
    mocker, plan_list_json, config, response, monkeypatch, tmp_path
):
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "plan", "list", "--limit", "1"])
    monkeypatch.setattr("sys.stdout.isatty", lambda: True)
    mocker.patch("builtins.input", side_effect=KeyboardInterrupt)
    response.status_code = 200
    response._content = plan_list_json
    list_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(SystemExit) as exit:
        tuxsuite.cli.main()
    assert exit.value.code == 0
    assert list_req.call_count == 1

    # Test --json
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "plan", "list", "--json"])
    response.status_code = 200
    response._content = plan_list_json
    list_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert exit.value.code == 0
    assert list_req.call_count == 1

    # Test --json-out
    json_path = f"{tmp_path}/plan.json"
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "plan", "list", "--json-out", json_path]
    )
    response.status_code = 200
    response._content = plan_list_json
    list_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert exit.value.code == 0
    assert list_req.call_count == 1
    assert len(json.load(open(json_path, "r"))) > 0

    # Test failure case when the response is not 200
    response.status_code = 500
    list_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(NotImplementedError):
        tuxsuite.cli.main()
    assert list_req.call_count == 1

    mocker.resetall()
    response.status_code = 200
    response._content = plan_list_json
    list_req = mocker.patch("requests.get", return_value=response)
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "plan", "list", "--limit", "1"],
    )
    with pytest.raises(SystemExit):
        tuxsuite.cli.main()
    assert list_req.call_count == 1


def test_bake_plan_handle_get(
    mocker, bake_plan_json, config, response, monkeypatch, tmp_path
):
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "plan", "get", "29EbSmPfjpbYQj8ZuaBpsiA8CbW"]
    )
    response.status_code = 200
    response._content = bake_plan_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1

    # Test --json
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "plan", "get", "29EbSmPfjpbYQj8ZuaBpsiA8CbW", "--json"],
    )
    response.status_code = 200
    response._content = bake_plan_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1

    # Test --json-out
    json_path = f"{tmp_path}/plan.json"
    mocker.resetall()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "plan",
            "get",
            "29EbSmPfjpbYQj8ZuaBpsiA8CbW",
            "--json-out",
            json_path,
        ],
    )
    response.status_code = 200
    response._content = bake_plan_json
    get_req = mocker.patch("requests.get", return_value=response)
    tuxsuite.cli.main()
    assert get_req.call_count == 1
    assert len(json.load(open(json_path, "r"))) > 0

    # Test failure case when the response is not 200
    response.status_code = 500
    get_req = mocker.patch("requests.get", return_value=response)
    with pytest.raises(NotImplementedError):
        tuxsuite.cli.main()
    assert get_req.call_count == 1


def test_plan_handle_create(
    build_plan,
    single_build_plan,
    test_plan,
    plan_config,
    monkeypatch,
    config,
    tmp_path,
    capsys,
):
    # case: No arguments
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "plan", "create"])
    with pytest.raises(SystemExit):
        tuxsuite.cli.main()
    _, err = capsys.readouterr()
    assert err == "Error: At least one of '--build-plan' or '--test-plan' is required\n"

    # case: Unknown Arguments
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "plan",
            "create",
            "--build-plan",
            build_plan,
            "--overrite-targets",
            "T1",
        ],
    )
    with pytest.raises(SystemExit):
        tuxsuite.cli.main()
    _, err = capsys.readouterr()
    assert err == "Error: Unknown option: ['--overrite-targets', 'T1']\n"

    # case: only build plan
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "plan", "create", "--build-plan", build_plan]
    )
    tuxsuite.cli.main()
    out, err = capsys.readouterr()
    assert err == ""

    # case: only build plan with --overwrite-target
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "plan",
            "create",
            "--build-plan",
            build_plan,
            "--overwrite-target",
            "tar1",
            "--overwrite-target",
            "tar2",
            "--overwrite-target",
            "tar3",
        ],
    )
    tuxsuite.cli.main()
    out, err = capsys.readouterr()
    data = yaml.load(out, Loader=yaml.FullLoader)
    assert err == ""
    assert data["jobs"][0]["build"]["targets"] == ["tar1", "tar2", "tar3"]

    # case: only build plan with --apend-kconfig (kconfig - str)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "plan",
            "create",
            "--build-plan",
            build_plan,
            "--append-kconfig",
            "config1",
            "--append-kconfig",
            "config2",
        ],
    )
    tuxsuite.cli.main()
    out, err = capsys.readouterr()
    data = yaml.load(out, Loader=yaml.FullLoader)
    assert err == ""
    assert data["jobs"][0]["build"]["kconfig"] == ["tinyconfig", "config1", "config2"]

    # case: only build plan with --apend-kconfig (kconfig - list)
    data = yaml.safe_load(single_build_plan)
    data["jobs"][0]["build"]["kconfig"] = ["tinyconfig", "configx"]
    plan_path = tmp_path / "new_build_plan.yaml"
    with open(plan_path, "w") as f:
        yaml.dump(data, f)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "plan",
            "create",
            "--build-plan",
            f"{plan_path}",
            "--append-kconfig",
            "config1",
            "--append-kconfig",
            "config2",
        ],
    )
    tuxsuite.cli.main()
    out, err = capsys.readouterr()
    data = yaml.load(out, Loader=yaml.FullLoader)
    assert err == ""
    assert data["jobs"][0]["build"]["kconfig"] == [
        "tinyconfig",
        "configx",
        "config1",
        "config2",
    ]

    # case: only build plan with both --overwrite-target  and --apend-kconfig
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "plan",
            "create",
            "--build-plan",
            build_plan,
            "--overwrite-target",
            "tar1",
            "--overwrite-target",
            "tar2",
            "--append-kconfig",
            "config1",
            "--append-kconfig",
            "config2",
        ],
    )
    tuxsuite.cli.main()
    out, err = capsys.readouterr()
    data = yaml.load(out, Loader=yaml.FullLoader)
    assert err == ""
    assert data["jobs"][0]["build"]["targets"] == ["tar1", "tar2"]
    assert data["jobs"][0]["build"]["kconfig"] == ["tinyconfig", "config1", "config2"]

    # case: plan with invalid build job
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "plan",
            "create",
            "--build-plan",
            str(plan_config),
        ],
    )
    with pytest.raises(SystemExit):
        tuxsuite.cli.main()
    _, err = capsys.readouterr()
    assert (
        err
        == "Error: The build plan file is invalid. It should only include one build job\n"
    )

    # case: only test plan
    monkeypatch.setattr(
        sys, "argv", ["tuxsuite", "plan", "create", "--test-plan", test_plan]
    )
    tuxsuite.cli.main()
    out, err = capsys.readouterr()
    assert err == ""

    # case: test plan with --overwrite-target
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "plan",
            "create",
            "--test-plan",
            test_plan,
            "--overwrite-target",
            "tar1",
            "--overwrite-target",
            "tar2",
            "--overwrite-target",
            "tar3",
        ],
    )
    with pytest.raises(SystemExit):
        tuxsuite.cli.main()
    _, err = capsys.readouterr()
    assert (
        err
        == "Error: '--build-plan' is necessary if '--overwrite-target' or '--append-kconfig' is provided\n"
    )

    # case: only test plan with --test-retrigger
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "plan",
            "create",
            "--test-plan",
            test_plan,
            "--test-retrigger",
            str(3),
        ],
    )
    tuxsuite.cli.main()
    out, err = capsys.readouterr()
    assert err == ""
    data = yaml.load(out, Loader=yaml.FullLoader)
    assert len(data["jobs"][0]["tests"]) == 3
    test_job = data["jobs"][0]["tests"][0]
    assert test_job["parameters"]["ITERATIONS"] == 2
    assert (
        test_job["parameters"]["PERF"]
        == "https://storage.tuxsuite.com/grp/prj/tests/uid/perf.tar.xz"
    )
    assert (
        test_job["dtb"]
        == "https://storage.tuxsuite.com/grp/prj/tests/uid/dtbs/am57xx-beagle-x15.dtb"
    )

    # case: plan with invalid test job
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "plan",
            "create",
            "--test-plan",
            str(plan_config),
        ],
    )
    with pytest.raises(SystemExit):
        tuxsuite.cli.main()
    _, err = capsys.readouterr()
    assert (
        err
        == "Error: The test plan file is invalid. It should only include one test job\n"
    )

    # case: only build plan with --output-plan
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "plan",
            "create",
            "--build-plan",
            build_plan,
            "--output-plan",
            str(tmp_path / "tux_plan.yaml"),
        ],
    )
    tuxsuite.cli.main()
    out, err = capsys.readouterr()
    assert err == ""
    data = open(f"{tmp_path}/tux_plan.yaml").read()
    assert data is not None

    # case: with build and test plan
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tuxsuite",
            "plan",
            "create",
            "--build-plan",
            build_plan,
            "--test-plan",
            test_plan,
            "--test-retrigger",
            str(2),
        ],
    )
    tuxsuite.cli.main()
    out, err = capsys.readouterr()
    assert err == ""
    data = yaml.safe_load(out)
    assert len(data["jobs"][0]["tests"]) == 2
    test_job = data["jobs"][0]["tests"][0]
    assert test_job["kernel"] is None
    assert test_job["modules"] is None
    assert test_job["parameters"]["ITERATIONS"] == 2
    assert test_job["parameters"]["PERF"] == "$BUILD/perf.tar.xz"
    assert test_job["parameters"]["KSELFTEST"] == "$BUILD/kselftest.tar.xz"
    assert test_job["dtb"] == "am57xx-beagle-x15.dtb"


def test_plan_get_pc_headers():
    from tuxsuite.cli.plan import get_cb_headers

    headers = ["X-First-Name: Senthil", "X-Last-Name: Kumaran"]
    headers_dict = {"X-First-Name": "Senthil", "X-Last-Name": "Kumaran"}
    h_dict = get_cb_headers(headers)
    assert headers_dict == h_dict


def test_plan_handle_execute(
    build_plan,
    monkeypatch,
    tmp_path,
    capsys,
    mocker,
):
    # case: No arguments
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "plan", "execute"])
    with pytest.raises(SystemExit):
        tuxsuite.cli.main()
    _, err = capsys.readouterr()
    assert "the following arguments are required: config" in err

    # case: Unknown Arguments
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "plan", "execute", "--arg", "arg", "arg2"],
    )
    with pytest.raises(SystemExit):
        tuxsuite.cli.main()
    _, err = capsys.readouterr()
    assert err == "Error: Unknown option: ['--arg', 'arg2']\n"

    # case: Unknown linux source tree
    mocker.patch("subprocess.call", return_value=1)
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "plan", "execute", build_plan, "-t", str(tmp_path)],
    )
    with pytest.raises(SystemExit):
        tuxsuite.cli.main()

    # case: Unknown unknown runtime
    monkeypatch.setattr(
        sys,
        "argv",
        ["tuxsuite", "plan", "execute", build_plan, "--runtime", "dockerr"],
    )
    with pytest.raises(SystemExit):
        tuxsuite.cli.main()
    _, err = capsys.readouterr()
    assert "argument -r/--runtime: invalid choice: 'dockerr' (choose from 'docker', 'podman')"

    # case: happy flow
    mocker.patch("subprocess.check_call")
    mocker.patch("subprocess.call", return_value=0)
    monkeypatch.setattr(sys, "argv", ["tuxsuite", "plan", "execute", build_plan])
    tuxsuite.cli.main()
    out, err = capsys.readouterr()
    assert err == ""
    assert "==> Submitting Local Plan" in out
