import json
import sys
import platformdirs
import keyring
import os
from pathlib import Path

class ConfigException(Exception):
    pass

CONFIG_FILE_DIR = platformdirs.user_config_dir('backupchan')
CONFIG_FILE_PATH = f"{CONFIG_FILE_DIR}/config.json"

class Config:
    def __init__(self, config_path: str | None = None):
        self.port: int | None = None
        self.host: str | None = None
        self.api_key: str | None = None
        self.custom_config_path = config_path

    def read_config(self):
        config_path = self.get_config_path()
        if not os.path.exists(config_path):
            raise ConfigException("Config file not found")

        with open(config_path, "r") as config_file:
            self.parse_config(config_file.read())
        self.retrieve_api_key()

    def reset(self, write: bool = False):
        self.port = None
        self.host = None
        self.api_key = None
        config_path = self.get_config_path()

        if write:
            self.delete_api_key()
            if os.path.exists(config_path):
                os.remove(config_path)

    def is_incomplete(self):
        return self.port is None or self.host is None or self.api_key is None

    def parse_config(self, config: str):
        config_json = json.loads(config)
        self.port = int(config_json["port"])
        self.host = config_json["host"]

    def retrieve_api_key(self):
        self.api_key = keyring.get_password("backupchan", "api_key")

    def save_config(self):
        config_path = self.get_config_path()
        if self.is_incomplete():
            raise ConfigException("Cannot save incomplete config")
        
        Path(self.get_config_file_dir()).mkdir(exist_ok=True, parents=True)

        config_dict = {
            "host": self.host,
            "port": self.port
        }

        with open(config_path, "w") as config_file:
            json.dump(config_dict, config_file)

        self.save_api_key()

    def delete_api_key(self):
        try:
            keyring.delete_password("backupchan", "api_key")
        except keyring.errors.PasswordDeleteError:
            pass
    
    def save_api_key(self):
        keyring.set_password("backupchan", "api_key", self.api_key)

    def get_config_path(self) -> str:
        if self.custom_config_path is None:
            return CONFIG_FILE_PATH
        return self.custom_config_path

    def get_config_file_dir(self) -> str:
        return os.path.dirname(self.get_config_path())
