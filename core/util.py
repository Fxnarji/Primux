import json
from pathlib import Path


class ConfigHelper:
    def __init__(self):
        config_path = Path(__file__).parent.parent / "config.json"
        print(config_path)
        self.config_path = config_path
        self._config = self.load_config()

    def load_config(self):
        if not self.config_path.exists():
            return {}
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get(self, key, default=None):
        return self._config.get(key, default)

    def write(self, key, value):
        self._config[key] = value
        self.save_config()

    def save_config(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self._config, f, indent=4)

