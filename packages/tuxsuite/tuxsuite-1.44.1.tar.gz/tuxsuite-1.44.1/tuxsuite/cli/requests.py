# -*- coding: utf-8 -*-

import requests

from tuxsuite.utils import is_down
from tuxsuite.cli.version import __version__


def headers(config):
    return {
        "User-Agent": f"tuxsuite.cli/{__version__}",
        "Authorization": config.token,
    }


def apiurl(config, url):
    return f"{config.tuxapi_url}{url}"


@is_down
def get(config, url, params=None):
    # print(f"GET {config.tuxapi_url}{url} {params=}")
    return requests.get(
        f"{config.tuxapi_url}{url}", headers=headers(config), params=params
    )


@is_down
def get_storage(config, url, params=None):
    # print(f"GET {config.tuxapi_url}{url} {params=}")
    return requests.get(f"{url}", headers=headers(config), params=params)


@is_down
def post(config, url, data):
    # print(f"POST {config.tuxapi_url}{url}")
    # print(f"POST {data}")
    return requests.post(
        f"{config.tuxapi_url}{url}", headers=headers(config), json=data
    )


@is_down
def delete(config, url, data):
    # print(f"DELETE {config.tuxapi_url}{url}")
    return requests.delete(
        f"{config.tuxapi_url}{url}", headers=headers(config), json=data
    )


@is_down
def put(config, url, data):
    # print(f"PUT {config.tuxapi_url}{url}")
    # print(f"PUT {data}")
    return requests.put(f"{config.tuxapi_url}{url}", headers=headers(config), json=data)
