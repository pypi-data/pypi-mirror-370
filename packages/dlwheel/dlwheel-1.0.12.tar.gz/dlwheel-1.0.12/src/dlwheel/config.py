import argparse
import time
from pathlib import Path

import yaml
from box import Box

from dlwheel.utils import get_timestamp_name


class ConfigLoader:
    def __init__(self):
        self._cfg = Box(default_box=True, default_box_attr=None, box_dots=True)

    def run(self):
        args = self._parse_args()
        self._load_config(args.config)
        self._overide_config(args)
        return self._cfg

    def _parse_args(self):
        parser = argparse.ArgumentParser(allow_abbrev=False)
        parser.add_argument("--config", default="config/default.yaml")
        parser.add_argument("--backup", action="store_true")
        parser.add_argument("--resume", action="store_true")
        parser.add_argument("--name", default=get_timestamp_name())
        parser.add_argument("--tmp", action="store_true")

        args, unk = parser.parse_known_args()

        if args.tmp:
            args.name = "_tmp"

        for arg in unk:
            k, _, v = arg.lstrip("-").partition("=")
            setattr(args, k, v if _ else True)
        return args

    def _load_config(self, config_path):
        if Path(config_path).exists():
            yaml_cfg = yaml.load(open(config_path), yaml.FullLoader)
            self._cfg.update(yaml_cfg)

    def _overide_config(self, args):
        for key, value in vars(args).items():
            *path, key = key.split(".")
            current = self._cfg
            for p in path:
                if current[p] is None:
                    current[p] = Box(
                        default_box=True, default_box_attr=None, box_dots=True
                    )
                current = current[p]
            current[key] = self._convert(value, current.get(key))

    def _convert(self, value, origin):
        try:
            return type(origin)(value) if origin else value
        except:
            return value
