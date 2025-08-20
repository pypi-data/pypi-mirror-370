import os
from dataclasses import dataclass
from io import BytesIO
from typing import Union

import paramiko
from azure.core.credentials import (
    AzureNamedKeyCredential,
    AzureSasCredential,
    TokenCredential,
)
from azure.storage.blob import ContainerProperties


@dataclass
class FileObjectData:
    file_data: bytes
    file_IO: BytesIO
    filename: str
    filepath: str | None = None
    mime_type: str | None = None
    metadata: dict[str, str] | None = None


@dataclass
class FileSystemFileReference:
    filepath: str

    @property
    def filename(self) -> str:
        return os.path.basename(self.filepath)

    @property
    def dirname(self) -> str:
        return os.path.dirname(self.filepath)


@dataclass
class RemoteObjectReference:
    file_id: str
    mime_type: str
    filename: str | None = None

    @property
    def is_dir(self) -> bool:
        return "folder" in self.mime_type


FileSystemObject = Union[FileSystemFileReference, RemoteObjectReference, FileObjectData]


FileTransfer = tuple[FileSystemObject, FileSystemObject]


class IncompatibleFileReference(Exception):
    pass


@dataclass(frozen=True, kw_only=True)
class FileSystemSFTPConfig:
    ip: str
    username: str
    pem_path: str | None
    pem_key: paramiko.RSAKey | None = None
    password: str | None = None
    valid_extensions: tuple[str] | None = None
    recursive: bool = True


@dataclass(kw_only=True)
class FileSystemS3Config:
    endpoint_url: str
    bucket_name: str
    region_name: str | None
    access_key_id: str | None
    secret_access_key: str | None
    session_token: str | None


@dataclass(kw_only=True)
class FileSystemBlobConfig:
    account_url: str
    credential: (
        str
        | dict[str, str]
        | AzureNamedKeyCredential
        | AzureSasCredential
        | TokenCredential
        | None
    )
    container: ContainerProperties | str
