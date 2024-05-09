import tomllib, os, logging


class ConfigBuilder:
    def __init__(self, entry_config):
        self.entry_config = entry_config
        self.config_files = []

        self.files = []
        self.build_scripts = set()
        self.user_scripts = set()

        self.logger = logging.getLogger(__name__)

    def build(self):
        try:
            self.collect_config_files()
        except FileNotFoundError as e:
            raise e

        for conf in self.config_files:
            data = self.load_file(conf)

            if data is None:
                continue

            for file in data.get("files", []):
                if "src" not in file:
                    raise KeyError(f"'src' key not found for file: {file}")
                if "dest" not in file:
                    raise KeyError(f"'dest' key not found for file: {file}")
                self.files.extend(
                    [{"src": self.abs_path(file["src"], conf), "dest": file["dest"]}]
                )

            self.build_scripts.update(
                [
                    self.abs_path(script, conf)
                    for script in data.get("scripts", {}).get("build", [])
                ]
            )
            self.user_scripts.update(
                [
                    self.abs_path(script, conf)
                    for script in data.get("scripts", {}).get("user", [])
                ]
            )

        return {
            "files": self.files,
            "scripts": {
                "build": list(self.build_scripts),
                "user": list(self.user_scripts),
            },
        }

    def collect_config_files(self):
        queue = [self.entry_config]

        while len(queue):
            current = queue.pop(0)

            if current in self.config_files:
                continue
            self.config_files.append(current)
            self.logger.info(f"Reading config: {current}")

            queue.extend(
                self.abs_path(module, current) for module in self.read_imports(current)
            )

    def abs_path(self, rel_path, parent):
        return os.path.normpath(os.path.join(os.path.dirname(parent), rel_path))

    def read_imports(self, conf):
        data = self.load_file(conf)

        return data.get("imports", []) if data else []

    def load_file(self, conf):
        try:
            with open(conf, "rb") as f:
                return tomllib.load(f)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File not found: {conf}") from e
