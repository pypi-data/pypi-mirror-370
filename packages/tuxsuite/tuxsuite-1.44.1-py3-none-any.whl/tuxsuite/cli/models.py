# -*- coding: utf-8 -*-

from dataclasses import asdict, dataclass, field, fields
from typing import Dict, List
import tuxsuite.cli.colors as colors
import json


class Base:
    def as_dict(self):
        return asdict(self)

    def as_json(self):
        return json.dumps(self.as_dict())

    @classmethod
    def new(cls, **kwargs):
        fields_names = [f.name for f in fields(cls)]
        i_kwargs = {}
        v_kwargs = {}
        for k in kwargs:
            if k in fields_names:
                v_kwargs[k] = kwargs[k]
            else:
                i_kwargs[k] = kwargs[k]

        return cls(**v_kwargs, extra=i_kwargs)


@dataclass
class Bill(Base):
    @dataclass
    class Count(Base):
        builds: int
        oebuilds: int
        plans: int
        tests: int

    @dataclass
    class Duration(Base):
        builds: int
        oebuilds: int
        tests: int

    group: str
    date: str
    count: Count
    duration: Duration
    extra: Dict

    def __post_init__(self):
        self.count = Bill.Count(**self.count)
        self.duration = Bill.Duration(**self.duration)


@dataclass
class Build(Base):
    project: str
    uid: str
    plan: str
    kconfig: List[str]
    target_arch: str
    toolchain: str
    build_name: str
    client_token: str
    environment: Dict
    make_variables: Dict
    targets: List[str]
    git_repo: str
    git_ref: str
    git_sha: str
    download_url: str
    kernel_image: str
    user: str
    state: str
    result: str
    waited_by: List[str]
    errors_count: int
    warnings_count: int
    provisioning_time: str
    running_time: str
    finished_time: str
    extra: Dict
    git_short_log: str = None
    sccache_hits: int = None
    duration: int = None
    build_status: str = None
    sccache_misses: int = None
    tuxbuild_status: str = None
    kernel_version: str = None
    kernel_image_name: str = None
    status_message: str = None
    git_describe: str = None

    def __lt__(self, other):
        return (self.target_arch, self.toolchain) < (other.target_arch, other.toolchain)

    def url(self):
        (grp, prj) = self.project.split("/")
        return f"/v1/groups/{grp}/projects/{prj}/builds/{self.uid}"

    def get_builds_message(self, icon, color, msg):
        return f"{self.uid} {icon} {color}{msg}{colors.reset} {self.target_arch}@{self.toolchain}"


@dataclass
class Group(Base):
    @dataclass
    class Count(Base):
        daily: int
        monthly: int
        overall: int

    @dataclass
    class Duration(Base):
        builds: int
        oebuilds: int
        tests: int

    name: str
    builds: Count
    oebuilds: Count
    plans: Count
    tests: Count
    duration: Duration
    limits: Duration
    lava_devices: List[str]
    extra: Dict

    def __lt__(self, other):
        return self.name < other.name

    def __post_init__(self):
        self.builds = Group.Count(**self.builds)
        self.oebuilds = Group.Count(**self.oebuilds)
        self.plans = Group.Count(**self.plans)
        self.tests = Group.Count(**self.tests)
        self.duration = Group.Duration(**self.duration)
        self.limits = Group.Duration(**self.limits)


@dataclass
class Test(Base):
    project: str
    device: str
    uid: str
    kernel: str
    modules: str
    tests: List[str]
    test_name: str
    state: str
    result: str
    results: Dict[str, str]
    plan: str
    waiting_for: str
    download_url: str
    provisioning_time: str
    running_time: str
    finished_time: str
    extra: Dict
    overlays: List = field(default_factory=list)
    waited_by: List = field(default_factory=list)
    duration: int = None
    boot_args: str = None
    user: str = None

    def __lt__(self, other):
        return self.device < other.device

    def url(self):
        (grp, prj) = self.project.split("/")
        return f"/v1/groups/{grp}/projects/{prj}/tests/{self.uid}"

    def as_dict(self):
        return asdict(self)

    def as_json(self):
        return json.dumps(self.as_dict())


@dataclass
class Bitbake(Base):
    project: str
    uid: str
    plan: str
    distro: str
    machine: str
    container: str
    environment: Dict
    local_conf: List[str]
    bblayers_conf: List[str]
    envsetup: str
    download_url: str
    user: str
    state: str
    result: str
    extra: Dict
    waited_by: List[str]
    errors_count: int
    warnings_count: int
    provisioning_time: str
    running_time: str
    finished_time: str
    targets: str = None
    target: str = None
    duration: int = None
    status_message: str = None
    manifest_file: str = None

    def __lt__(self, other):
        pass

    def url(self):
        (grp, prj) = self.project.split("/")
        return f"/v1/groups/{grp}/projects/{prj}/oebuilds/{self.uid}"

    def get_builds_message(self, icon, color, msg):
        return (
            f"{self.uid} {icon} {color}{msg}{colors.reset} with container {self.container} "
            f"and machine {self.machine}"
        )


@dataclass
class Plan(Base):
    project: str
    uid: str
    name: str
    description: str
    extra: Dict
    builds: List = field(default_factory=list)
    tests: List = field(default_factory=list)
    oebuilds: List = field(default_factory=list)
    provisioning_time: str = None
    user: str = None
    all_builds: List = field(default_factory=list)

    def __post_init__(self):
        if self.builds or self.oebuilds:
            self.all_builds = [Build.new(**b) for b in self.builds["results"]] + [
                Bitbake.new(**oeb) for oeb in self.oebuilds["results"]
            ]

        if self.tests:
            self.tests = [Test.new(**t) for t in self.tests["results"]]

    def as_dict(self):
        return asdict(self)

    def as_json(self):
        return json.dumps(self.as_dict())

    def _dependent_tests(self, uid):
        return [
            t
            for t in self.tests
            if t.waiting_for and t.waiting_for.split("#")[1] == uid
        ]

    def _tests_wait_for(self, build_uid, get_sanity=False):
        sanity_test = None
        tests = self._dependent_tests(build_uid)
        if len(tests) == 1 and tests[0].waited_by:
            sanity_test = tests[0]
            tests = self._dependent_tests(sanity_test.uid)
        return (tests, sanity_test) if get_sanity else tests

    def filter_builds(self, f):
        return sorted([b for b in self.all_builds if f(self, b)])

    def filter_tests(self, f):
        return sorted([t for t in self.tests if f(self, t)])

    def passing(self):
        def __filter(plan, build):
            return (build.result == "pass" and build.warnings_count == 0) and (
                all([t.result == "pass" for t in plan._tests_wait_for(build.uid)])
            )

        return self.filter_builds(__filter)

    def warning(self):
        def __filter(plan, build):
            return (build.result == "pass" and build.warnings_count != 0) and (
                all([t.result == "pass" for t in self._tests_wait_for(build.uid)])
            )

        return self.filter_builds(__filter)

    def failing(self):
        def __filter(plan, build):
            return build.result == "fail" or any(
                [t.result == "fail" for t in self._tests_wait_for(build.uid)]
            )

        return self.filter_builds(__filter)

    def errors(self):
        def __filter(plan, build):
            return build.result == "error" or any(
                [t.result == "error" for t in self._tests_wait_for(build.uid)]
            )

        return self.filter_builds(__filter)

    def canceled(self):
        def __filter(plan, build):
            return build.result == "canceled"

        return self.filter_builds(__filter)

    def unknown(self):
        def __filter(plan, build):
            return build.result == "unknown"

        return self.filter_builds(__filter)
