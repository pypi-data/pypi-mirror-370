import os
import json
from pathlib import Path

class WiFiScannerConfig:
    def __init__(self):
        self.config_file = os.path.expanduser('~/.py_wifi_helper.json')
        self._load_config()

    def _load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                self._config = json.load(f)
        except FileNotFoundError:
            self._config = {}
            self._save_config()

    def _save_config(self):
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self._config, f, indent=2)

    @property
    def scanner_app_path(self):
        return self._config.get('scanner_app_path')

    @scanner_app_path.setter
    def scanner_app_path(self, path):
        if path:
            path = os.path.expanduser(path)
            if not path.endswith('.app'):
                path = os.path.join(path, 'WiFiScanner.app')
        self._config['scanner_app_path'] = path
        self._save_config()
