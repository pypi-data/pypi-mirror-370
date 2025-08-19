# -*- coding: utf-8 -*-

import sys


from attr import attrs, attrib
from requests.exceptions import HTTPError


def error(msg):
    sys.stderr.write(f"Error: {msg}\n")
    sys.exit(1)


class defaults:
    targets = [
        "config",
        "debugkernel",
        "dtbs",
        "kernel",
        "modules",
        "xipkernel",
    ]


@attrs(kw_only=True)
class ResultState:
    state = attrib()
    status = attrib(default=None)
    message = attrib()
    warnings = attrib(default=0)
    errors = attrib(default=0)
    icon = attrib()
    cli_color = attrib()
    final = attrib(default=False)


result_states = {
    "queued": ResultState(
        state="queued",
        message="Queued",
        icon="⏳",
        cli_color="white",
    ),
    "waiting": ResultState(
        state="waiting",
        message="Waiting",
        icon="⏳",
        cli_color="white",
    ),
    "provisioning": ResultState(
        state="provisioning",
        message="Provisioning",
        icon="⚙️ ",
        cli_color="white",
    ),
    "building": ResultState(
        state="building",
        message="Building",
        icon="🚀",
        cli_color="cyan",
    ),
    "running": ResultState(
        state="running",
        message="Running",
        icon="🚀",
        cli_color="cyan",
    ),
}


def is_down(func):
    def wrapper(*args, **kwargs):
        try:
            ret = func(*args, **kwargs)
            ret.raise_for_status()
        except HTTPError as exc:
            if exc.response.status_code == 503:
                error(exc)
        return ret

    return wrapper
