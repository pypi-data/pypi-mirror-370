import os
from io import BytesIO

from pkgs.filesystem_utils.file_type_utils import (
    FileObjectData,
    FileSystemFileReference,
    FileSystemObject,
    FileTransfer,
    IncompatibleFileReference,
)

from .filesystem_session import FileSystemSession


class LocalSession(FileSystemSession):
    def __init__(self) -> None:
        super().__init__()

    def start(self) -> None:
        return None

    def __enter__(self) -> "LocalSession":
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        return None

    def move_files(self, file_mappings: list[FileTransfer]) -> None:
        for src_file, dest_file in file_mappings:
            if not (
                isinstance(src_file, FileSystemFileReference)
                and isinstance(dest_file, FileSystemFileReference)
            ):
                raise IncompatibleFileReference()
            os.rename(src_file.filepath, dest_file.filepath)

    def download_files(self, filepaths: list[FileSystemObject]) -> list[FileObjectData]:
        downloaded_files: list[FileObjectData] = []
        for file_object in filepaths:
            if (
                not isinstance(file_object, FileSystemFileReference)
                or file_object.filename is None
            ):
                raise IncompatibleFileReference()
            with open(file_object.filepath, "rb") as file_data:
                file_bytes = file_data.read()
            downloaded_files.append(
                FileObjectData(
                    file_bytes,
                    BytesIO(file_bytes),
                    file_object.filename,
                    filepath=file_object.filepath,
                )
            )
        return downloaded_files

    def list_files(
        self, dir_path: FileSystemObject, *, recursive: bool = False
    ) -> list[FileSystemObject]:
        if not isinstance(dir_path, FileSystemFileReference) or not os.path.isdir(
            dir_path.filepath
        ):
            raise IncompatibleFileReference()
        if recursive:
            raise NotImplementedError("recursive not implemented for local session")
        return [
            FileSystemFileReference(os.path.join(dir_path.filepath, filename))
            for filename in os.listdir(dir_path.filepath)
        ]
