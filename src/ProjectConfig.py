from src.ConfigFile import ConfigFile


def config() -> dict:
    return ConfigFile("config.toml").data
