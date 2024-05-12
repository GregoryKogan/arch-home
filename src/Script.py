import os


class Script:
    def __init__(self, name: str, data: dict[str, any], parent_path: str):
        self.__name = name
        self.__data = data
        self.__parent_path = parent_path

        self.__validate()

    @property
    def name(self) -> str:
        return self.__name

    @property
    def parent_path(self) -> str:
        return self.__parent_path

    @property
    def source(self) -> str:
        if "src" in self.__data:
            relative = self.__data["src"]
            return self.absolute_path(relative, self.parent_path)
        return None

    @property
    def text(self) -> str:
        return self.__data.get("text", None)

    @property
    def user(self) -> bool:
        return self.__data.get("user", False)

    @property
    def stage(self) -> int:
        return self.__data.get("stage", 0)

    @property
    def build(self) -> bool:
        return self.__data.get("build", True)

    def __validate(self) -> None:
        if self.source is None and self.text is None:
            raise ValueError(f"Source or text not found in Script: {self.name}")

        if self.source is not None and self.text is not None:
            raise ValueError(f"Both source and text found in Script: {self.name}")

        if self.source is not None and not isinstance(self.source, str):
            raise ValueError(f"Source must be a string: {self.name}")

        if self.text is not None and not isinstance(self.text, str):
            raise ValueError(f"Text must be a string: {self.name}")

        if not isinstance(self.user, bool):
            raise ValueError(f"User must be a boolean: {self.name}")

        if not isinstance(self.build, bool):
            raise ValueError(f"Build must be a boolean: {self.name}")

        if not isinstance(self.stage, int):
            raise ValueError(f"Stage must be an integer: {self.name}")

    @staticmethod
    def absolute_path(relative_path, parent):
        return os.path.normpath(os.path.join(os.path.dirname(parent), relative_path))
