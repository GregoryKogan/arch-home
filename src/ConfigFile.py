import tomllib


class ConfigFile:
    def __init__(self, path: str):
        self.__path = path
        self.__data = {}

        self.load()

    @property
    def path(self) -> str:
        return self.__path

    @property
    def data(self) -> dict:
        return self.__data

    def load(self) -> None:
        try:
            with open(self.__path, "rb") as f:
                self.__data = tomllib.load(f)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Config file not found: {self.__path}") from e
