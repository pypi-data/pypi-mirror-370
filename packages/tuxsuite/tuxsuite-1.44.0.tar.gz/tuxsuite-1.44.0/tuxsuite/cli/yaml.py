# -*- coding: utf-8 -*-

import yaml

YamlError = yaml.YAMLError

try:
    from yaml import CFullLoader as FullLoader
except ImportError:
    from yaml import FullLoader

    print("Warning: using python yaml loader")


def yaml_load(data, safe=False):
    if safe:
        return yaml.safe_load(data)
    return yaml.load(data, Loader=FullLoader)


def yaml_dump(data, dump_file=None, sort_keys=True):
    return yaml.dump(data, dump_file, sort_keys=sort_keys)
