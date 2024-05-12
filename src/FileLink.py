import os


class FileLink:
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
        relative = self.__data["src"]
        return self.absolute_path(relative, self.parent_path)

    @property
    def destination(self) -> str:
        relative = self.__data["dest"]
        return os.path.join(os.path.expanduser("~"), relative)

    @property
    def link_pre(self) -> bool:
        return self.__data.get("link-pre", True)

    @property
    def link_post(self) -> bool:
        return self.__data.get("link-post", False)

    def __validate(self) -> None:
        if "src" not in self.__data:
            raise ValueError(f"Source not found in FileLink: {self.name}")

        if "dest" not in self.__data:
            raise ValueError(f"Destination not found in FileLink: {self.name}")

        if not isinstance(self.source, str):
            raise ValueError(f"Source must be a string: {self.name}")

        if not isinstance(self.destination, str):
            raise ValueError(f"Destination must be a string: {self.name}")

        if not isinstance(self.link_pre, bool):
            raise ValueError(f"Link pre must be a boolean: {self.name}")

        if not isinstance(self.link_post, bool):
            raise ValueError(f"Link post must be a boolean: {self.name}")

    @staticmethod
    def absolute_path(relative_path, parent):
        return os.path.normpath(os.path.join(os.path.dirname(parent), relative_path))
