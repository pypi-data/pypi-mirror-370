from abc import ABC, abstractmethod

from pkgs.filesystem_utils.file_type_utils import (
    FileObjectData,
    FileSystemObject,
    FileTransfer,
)


class FileSystemSession(ABC):
    def __init__(self) -> None:
        return

    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_files(
        self, dir_path: FileSystemObject, *, recursive: bool = True
    ) -> list[FileSystemObject]:
        raise NotImplementedError

    @abstractmethod
    def move_files(self, file_mappings: list[FileTransfer]) -> None:
        raise NotImplementedError

    @abstractmethod
    def download_files(self, filepaths: list[FileSystemObject]) -> list[FileObjectData]:
        raise NotImplementedError

    def delete_files(self, filepaths: list[FileSystemObject]) -> None:
        raise NotImplementedError

    @abstractmethod
    def __enter__(self) -> "FileSystemSession": ...

    @abstractmethod
    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None: ...
