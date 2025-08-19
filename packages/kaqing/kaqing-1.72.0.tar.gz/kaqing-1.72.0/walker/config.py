import importlib
import os
from typing import TypeVar, cast
import yaml
from pathlib import Path

from . import __version__
from walker.utils import get_deep_keys, log2

T = TypeVar('T')

class Config:
    EMBEDDED_PARAMS = {}

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Config, cls).__new__(cls)

        return cls.instance

    def __init__(self, path: str = None, is_user_entry = False):
        if path:
            try:
                with open(path) as f:
                    self.params = cast(dict[str, any], yaml.safe_load(f))
            except:
                self.copy_config_file(is_user_entry=is_user_entry)
        elif not hasattr(self, 'params'):
            self.copy_config_file(is_user_entry=is_user_entry)

    def copy_config_file(self, is_user_entry = False):
        dir = f'{Path.home()}/.kaqing'
        path = f'{dir}/params.yaml.{__version__}'
        if not os.path.exists(path):
            os.makedirs(dir, exist_ok=True)
            module = importlib.import_module('walker.embedded_params')
            with open(path, 'w') as f:
                yaml.dump(module.params(), f, default_flow_style=False)
            if not is_user_entry:
                log2(f'Default params.yaml has been written to {path}.')

        with open(path) as f:
            self.params = cast(dict[str, any], yaml.safe_load(f))

        return path

    def action_node_samples(self, action: str, default: T):
        return self.get(f'{action}.samples', default)

    def action_workers(self, action: str, default: T):
        return self.get(f'{action}.workers', default)

    def keys(self) -> list[str]:
        return get_deep_keys(self.params)

    def get(self, key: str, default: T) -> T:
        # params['nodetool']['status']['max-nodes']
        d = self.params
        for p in key.split("."):
            if p in d:
                d = d[p]
            else:
                return default

        return d

    def set(self, key: str, v: str):
        d = Config().params
        ps = key.split('.')
        for p in ps[:len(ps) - 1]:
            if p in d:
                d = d[p]
            else:
                log2(f'incorrect path: {key}')
                return None

        try:
            # check if a number
            v = int(v)
        except:
            # check if a boolean
            if v:
                vb = v.strip().lower()
                if vb == 'true':
                    v = True
                elif vb == 'false':
                    v = False

        p = ps[len(ps) - 1]
        if p in d:
            d[p] = v
        else:
            log2(f'incorrect path: {key}')
            return None

        return v if v else 'false'