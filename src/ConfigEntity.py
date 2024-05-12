import os, logging
from src.ConfigFile import ConfigFile
from src.ProjectConfig import config
from src.FileLink import FileLink
from src.Script import Script


logger = logging.getLogger("Universal Home Builder")


class ConfigEntity:
    def __init__(
        self, config_file: ConfigFile, ancestors: set[str] = None, hostname: str = None
    ):
        self.__config_file = config_file
        self.__ancestors = ancestors if ancestors is not None else set()
        self.__hostname = hostname

        self.__imports: list[ConfigEntity] = []
        self.__file_links: list[FileLink] = []
        self.__scripts: list[Script] = []

        self.__build()

    @property
    def config_file(self) -> ConfigFile:
        return self.__config_file

    @property
    def hostname(self) -> str:
        return self.__hostname

    @property
    def imports(self) -> list["ConfigEntity"]:
        return self.__imports

    @property
    def file_links(self) -> list[FileLink]:
        return self.__file_links

    @property
    def scripts(self) -> list[Script]:
        return self.__scripts

    def __build(self) -> None:
        logger.debug(f"Building ConfigEntity: {self.config_file.path}")
        self.__check_host()
        self.__build_imports()
        self.__build_file_links()
        self.__build_scripts()

    def __check_host(self) -> None:
        logger.debug(f"Checking host: {self.config_file.path}")
        self.check_host_existence()
        if self.hostname is not None:
            return

        host_config = self.config_file.data["host"]
        host_name = host_config.get("name", None)
        if host_name is None:
            raise ValueError(f"Host name not found: {self.config_file.path}")
        self.__hostname = host_name

    def __build_imports(self) -> None:
        logger.debug(f"Building imports: {self.config_file.path}")
        relative_imports = self.config_file.data.get("imports", [])
        relative_imports = self.join_default_module_path(relative_imports)

        absolute_imports = [
            self.absolute_path(imp, self.config_file.path) for imp in relative_imports
        ]

        if self.config_file.path in absolute_imports:
            raise ValueError(f"Self import not allowed: {self.config_file.path}")

        if len(absolute_imports) != len(set(absolute_imports)):
            raise ValueError(f"Duplicate imports found: {self.config_file.path}")

        if any(imp in self.__ancestors for imp in absolute_imports):
            raise ValueError(f"Circular imports found: {self.config_file.path}")

        children_ancestors = self.__ancestors | {self.config_file.path}
        self.__imports = [
            ConfigEntity(
                ConfigFile(imp), ancestors=children_ancestors, hostname=self.hostname
            )
            for imp in absolute_imports
        ]

    def __build_file_links(self) -> None:
        logger.debug(f"Building file links: {self.config_file.path}")
        files = self.config_file.data.get("files", {})
        host_files = self.config_file.data.get(self.hostname, {}).get("files", {})

        self.__file_links = [
            FileLink(name, data, self.config_file.path)
            for name, data in {**files, **host_files}.items()
        ]

    def __build_scripts(self) -> None:
        logger.debug(f"Building scripts: {self.config_file.path}")
        scripts = self.config_file.data.get("scripts", {})
        host_scripts = self.config_file.data.get(self.hostname, {}).get("scripts", {})

        self.__scripts = [
            Script(name, data, self.config_file.path)
            for name, data in {**scripts, **host_scripts}.items()
        ]

    def check_host_existence(self) -> None:
        host_config = self.config_file.data.get("host", None)
        imported = self.hostname is not None

        if imported and host_config is not None:
            raise ValueError(f"Host can't be imported: {self.config_file.path}")

        if not imported and host_config is None:
            raise ValueError(f"Host not found: {self.config_file.path}")

    @staticmethod
    def absolute_path(relative_path, parent) -> str:
        return os.path.normpath(os.path.join(os.path.dirname(parent), relative_path))

    @staticmethod
    def join_default_module_path(imports: str) -> list[str]:
        default_module_filename = config().get("default-module-filename", "module.toml")
        return [
            imp if imp.endswith(".toml") else os.path.join(imp, default_module_filename)
            for imp in imports
        ]
