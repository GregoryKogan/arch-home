import os
from src.ConfigFile import ConfigFile


def config() -> dict:
    config_path = os.path.join(os.path.dirname(__file__), "../config.toml")
    return ConfigFile(config_path).data
