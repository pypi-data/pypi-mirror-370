import os
from tomllib import load as load_toml


class ConfigCache:
    def __init__(self):
        self._config = {
            "bind": "0.0.0.0",
            "port": 8080,
            "enforce": False,
            "admin_login": "admin",
            "admin_password": None,
            "user_login": "user",
            "user_password": None,
            "tasks": "./tasks",
            "cycle": 5,
            "logs": "./log",
            "log_rotate_when": "midnight",
            "log_rotate_interval": 1,
            "log_backup_count": 5,
        }
        if os.path.exists("suvi.toml") and os.path.isfile("suvi.toml"):
            with open("suvi.toml", "rb") as toml_pt:
                self._config = {**self._config, **load_toml(toml_pt)}

    def __getitem__(self, key):
        return self._config[key]

    def __setitem__(self, key, value):
        self._config[key] = value

    def __delitem__(self, key):
        del self._config[key]

    def __contains__(self, key):
        return key in self._config

    def __len__(self):
        return len(self._config)

    def __iter__(self):
        return iter(self._config)

    def keys(self):
        return self._config.keys()

    def values(self):
        return self._config.values()

    def items(self):
        return self._config.items()

    def get(self, key, default=None):
        return self._config.get(key, default)

    def pop(self, key, default=None):
        return self._config.pop(key, default)

    def clear(self):
        self._config.clear()

    def update(self, other):
        self._config.update(other)
