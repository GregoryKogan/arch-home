import os
from src.ConfigFile import ConfigFile
from src.ProjectConfig import config


class ConfigEntity:
    def __init__(self, config_file: ConfigFile, hostname: str = None):
        self.__config_file = config_file
        self.__hostname = hostname

        self.__imports: list[ConfigEntity] = []

        self.__build()

    @property
    def config_file(self) -> ConfigFile:
        return self.__config_file

    @property
    def hostname(self) -> str:
        return self.__hostname

    def __build(self) -> None:
        self.__check_host()
        self.__build_imports()

        for imp in self.__imports:
            print(imp.config_file.path)

    def __build_imports(self) -> None:
        relative_imports = self.config_file.data.get("imports", [])
        relative_imports = self.join_default_module_path(relative_imports)

        absolute_imports = [
            self.absolute_path(imp, self.config_file.path) for imp in relative_imports
        ]
        self.__imports = [
            ConfigEntity(ConfigFile(imp), hostname=self.hostname)
            for imp in absolute_imports
        ]

    def __check_host(self) -> None:
        self.check_host_existence()
        if self.hostname is not None:
            return

        host_config = self.config_file.data["host"]
        host_name = host_config.get("name", None)
        if host_name is None:
            raise ValueError(f"Host name not found: {self.config_file.path}")
        self.__hostname = host_name

    @staticmethod
    def absolute_path(relative_path, parent):
        return os.path.normpath(os.path.join(os.path.dirname(parent), relative_path))

    @staticmethod
    def join_default_module_path(imports: str) -> list[str]:
        default_module_filename = config().get("default-module-filename", "module.toml")
        return [
            imp if imp.endswith(".toml") else os.path.join(imp, default_module_filename)
            for imp in imports
        ]

    def check_host_existence(self) -> None:
        host_config = self.config_file.data.get("host", None)
        imported = self.hostname is not None

        if imported and host_config is not None:
            raise ValueError(f"Host can't be imported: {self.config_file.path}")

        if not imported and host_config is None:
            raise ValueError(f"Host not found: {self.config_file.path}")
