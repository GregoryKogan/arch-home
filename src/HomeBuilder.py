import os, subprocess, logging
from src.ProjectConfig import config
from src.ConfigEntity import ConfigEntity
from src.FileLink import FileLink
from src.Script import Script


logger = logging.getLogger("Universal Home Builder")


class HomeBuilder:
    def __init__(self, config_entity: ConfigEntity):
        self.__config_entity = config_entity

        self.__link_pre_queue = []
        self.__link_post_queue = []
        self.__build_scripts_queue = []
        self.__user_scripts_queue = []

    def build(self) -> None:
        logger.info("Building home directory")
        self.__populate_queues()
        self.__link_pre_files()
        self.__run_build_scripts()
        self.__link_post_files()
        self.__link_user_scripts()

    def __populate_queues(self) -> None:
        logger.debug("Populating queues")
        config_entities_queue = [self.__config_entity]
        while len(config_entities_queue):
            config_entity = config_entities_queue.pop(0)

            for file_link in config_entity.file_links:
                if file_link.pre:
                    self.__link_pre_queue.append(file_link)
                if file_link.post:
                    self.__link_post_queue.append(file_link)

            for script in config_entity.scripts:
                if script.build:
                    self.__build_scripts_queue.append(script)
                if script.user:
                    self.__user_scripts_queue.append(script)

            config_entities_queue.extend(config_entity.imports)

        self.__build_scripts_queue.sort(key=lambda script: script.stage)

    def __link_pre_files(self) -> None:
        logger.info("Pre-linking files")
        for file_link in self.__link_pre_queue:
            self.link_file(file_link)

    def __run_build_scripts(self) -> None:
        logger.info("Running build scripts")

        cur_stage = self.__build_scripts_queue[0].stage
        logger.info(f"Running stage: {cur_stage}")
        for script in self.__build_scripts_queue:
            if script.stage != cur_stage:
                cur_stage = script.stage
                logger.info(f"Running stage: {cur_stage}")

            logger.info(f"Running build script: {script.full_name}")
            content = script.text if script.text is not None else script.source
            subprocess.run([content], check=True, shell=True)

    def __link_post_files(self) -> None:
        logger.info("Post-linking files")
        for file_link in self.__link_post_queue:
            self.link_file(file_link)

    def __link_user_scripts(self) -> None:
        logger.info("Linking user scripts")
        script_dir = config().get("user-scripts-bin", "~/.bin")
        os.makedirs(os.path.expanduser(script_dir), mode=0o777, exist_ok=True)

        for script in self.__user_scripts_queue:
            logger.info(f"Linking user script: {script.name}")
            os.chmod(script.source, 0o755)
            destination = os.path.expanduser(
                os.path.join(script_dir, os.path.basename(script.source))
            )
            self.force_symlink(script.source, destination)

        self.check_environment_path()

    @staticmethod
    def link_file(file_link: FileLink) -> None:
        logger.info(f"Linking {file_link.full_name}")
        HomeBuilder.force_symlink(file_link.source, file_link.destination)

    @staticmethod
    def force_symlink(source: str, destination: str) -> None:
        logger.debug(f"Symlink: {destination} -> {source}")
        try:
            if os.path.exists(destination):
                os.remove(destination)
            os.symlink(source, destination)
        except Exception as e:
            raise RuntimeError(
                f"Failed to create symlink: {destination} -> {source}"
            ) from e

    @staticmethod
    def check_environment_path() -> None:
        script_dir = config().get("user-scripts-bin", "~/.bin")
        full_dir = os.path.expanduser(script_dir)
        if full_dir not in os.environ["PATH"].split(":"):
            logger.warning(f"Don't forget to add {script_dir} to your PATH")
