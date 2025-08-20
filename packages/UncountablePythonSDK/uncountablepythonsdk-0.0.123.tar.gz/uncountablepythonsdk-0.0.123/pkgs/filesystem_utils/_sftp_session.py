import os
from collections.abc import Iterable
from io import BytesIO

import paramiko
import pysftp

from pkgs.filesystem_utils.file_type_utils import (
    FileObjectData,
    FileSystemFileReference,
    FileSystemObject,
    FileSystemSFTPConfig,
    FileTransfer,
    IncompatibleFileReference,
)

from .filesystem_session import FileSystemSession


def move_sftp_files(
    connection: pysftp.Connection,
    src_filepath: str,
    dest_filepath: str,
) -> None:
    connection.rename(src_filepath, dest_filepath)


def list_sftp_files(
    connection: pysftp.Connection,
    dir_path: str,
    *,
    valid_extensions: Iterable[str] | None = None,
    parent_dir_path: str | None = None,
    recursive: bool = True,
) -> list[str]:
    file_paths: list[str] = []
    if recursive:

        def _skip(name: str) -> None:
            return

        def _add_file(path: str) -> None:
            if (
                valid_extensions is None
                or os.path.splitext(path)[1] in valid_extensions
            ) and (parent_dir_path is None or os.path.dirname(path) == parent_dir_path):
                file_paths.append(path)

        connection.walktree(
            dir_path, fcallback=_add_file, dcallback=_skip, ucallback=_skip
        )
    else:
        file_paths.extend([
            os.path.join(dir_path, file)
            for file in connection.listdir(dir_path)
            if connection.isfile(os.path.join(dir_path, file))
            and (
                valid_extensions is None
                or os.path.splitext(file)[1] in valid_extensions
            )
        ])
    return file_paths


class SFTPSession(FileSystemSession):
    def __init__(self, sftp_config: FileSystemSFTPConfig) -> None:
        super().__init__()
        self.host: str = sftp_config.ip
        self.username: str = sftp_config.username
        self.key_file: str | paramiko.RSAKey | None = (
            sftp_config.pem_path
            if sftp_config.pem_path is not None
            else sftp_config.pem_key
        )
        self.password: str | None = sftp_config.password

    def start(self) -> None:
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        if self.key_file is not None:
            self.connection = pysftp.Connection(
                self.host,
                username=self.username,
                private_key=self.key_file,
                cnopts=cnopts,
            )
        elif self.password is not None:
            self.connection = pysftp.Connection(
                self.host,
                username=self.username,
                password=self.password,
                cnopts=cnopts,
            )
        else:
            raise pysftp.CredentialException(
                "Must specify either a private key path or a password."
            )

    def __enter__(self) -> "SFTPSession":
        self.start()
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.connection.close()

    def list_files(
        self,
        dir_path: FileSystemObject,
        *,
        recursive: bool = True,
        valid_extensions: list[str] | None = None,
    ) -> list[FileSystemObject]:
        if not isinstance(
            dir_path, FileSystemFileReference
        ) or not self.connection.isdir(dir_path.filepath):
            raise IncompatibleFileReference()

        return [
            FileSystemFileReference(file_path)
            for file_path in list_sftp_files(
                self.connection,
                dir_path.filepath,
                recursive=recursive,
                valid_extensions=valid_extensions,
            )
        ]

    def download_files(self, filepaths: list[FileSystemObject]) -> list[FileObjectData]:
        downloaded_files: list[FileObjectData] = []
        for file_object in filepaths:
            if (
                not isinstance(file_object, FileSystemFileReference)
                or file_object.filename is None
            ):
                raise IncompatibleFileReference()
            filepath = file_object.filepath
            file_data = self.connection.open(filepath).read()
            downloaded_file = FileObjectData(
                file_data, BytesIO(file_data), file_object.filename, filepath=filepath
            )
            if downloaded_file is not None:
                downloaded_files.append(downloaded_file)
        return downloaded_files

    def move_files(self, file_mappings: list[FileTransfer]) -> None:
        for src_file, dest_file in file_mappings:
            if not isinstance(src_file, FileSystemFileReference) or not isinstance(
                dest_file, FileSystemFileReference
            ):
                raise IncompatibleFileReference()
            move_sftp_files(self.connection, src_file.filepath, dest_file.filepath)
