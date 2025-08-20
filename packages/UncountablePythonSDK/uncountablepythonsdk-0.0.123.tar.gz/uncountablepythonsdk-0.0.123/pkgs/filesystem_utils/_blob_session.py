from io import BytesIO

from azure.core.credentials import AzureSasCredential
from azure.storage.blob import BlobServiceClient, ContainerClient

from pkgs.filesystem_utils.file_type_utils import (
    FileObjectData,
    FileSystemBlobConfig,
    FileSystemFileReference,
    FileSystemObject,
    FileTransfer,
    IncompatibleFileReference,
)

from .filesystem_session import FileSystemSession


def _add_slash(prefix: str) -> str:
    if len(prefix) > 0 and prefix[-1] != "/":
        prefix = prefix + "/"
    return prefix


class BlobSession(FileSystemSession):
    config: FileSystemBlobConfig

    def __init__(self, blob_config: FileSystemBlobConfig) -> None:
        super().__init__()
        self.config = blob_config

    def start(self) -> None:
        self.service_client: BlobServiceClient | None = BlobServiceClient(
            self.config.account_url, credential=self.config.credential
        )
        self.container_client: ContainerClient | None = (
            self.service_client.get_container_client(self.config.container)
        )

    def __enter__(self) -> "BlobSession":
        self.start()
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.service_client = None
        self.container_client = None

    def list_files(
        self,
        dir_path: FileSystemObject,
        *,
        recursive: bool = False,
        valid_extensions: list[str] | None = None,
    ) -> list[FileSystemObject]:
        if not isinstance(dir_path, FileSystemFileReference):
            raise IncompatibleFileReference()

        assert self.service_client is not None and self.container_client is not None, (
            "call to list_files on uninitialized blob session"
        )

        filesystem_file_references: list[FileSystemObject] = []
        prefix = _add_slash(dir_path.filepath)
        for blob in self.container_client.list_blobs(name_starts_with=prefix):
            if not recursive and (
                blob.name == prefix or "/" in blob.name[len(prefix) :]
            ):
                continue
            if valid_extensions is None or any(
                blob.name.endswith(valid_extension)
                for valid_extension in valid_extensions
            ):
                filesystem_file_references.append(
                    FileSystemFileReference(
                        filepath=blob.name,
                    )
                )

        return filesystem_file_references

    def download_files(
        self,
        filepaths: list[FileSystemObject],
    ) -> list[FileObjectData]:
        downloaded_files: list[FileObjectData] = []
        assert self.service_client is not None and self.container_client is not None, (
            "call to download_files on uninitialized blob session"
        )

        for file_object in filepaths:
            if (
                not isinstance(file_object, FileSystemFileReference)
                or file_object.filename is None
            ):
                raise IncompatibleFileReference()

            blob_client = self.container_client.get_blob_client(file_object.filepath)
            download_stream = blob_client.download_blob()
            file_data = download_stream.readall()
            downloaded_files.append(
                FileObjectData(
                    file_data=file_data,
                    file_IO=BytesIO(file_data),
                    filename=file_object.filename,
                    filepath=file_object.filepath,
                )
            )

        return downloaded_files

    def move_files(self, file_mappings: list[FileTransfer]) -> None:
        assert self.service_client is not None and self.container_client is not None, (
            "call to move_files on uninitialized blob session"
        )

        for src_file, dest_file in file_mappings:
            if not isinstance(src_file, FileSystemFileReference) or not isinstance(
                dest_file, FileSystemFileReference
            ):
                raise IncompatibleFileReference()

            source_blob_client = self.container_client.get_blob_client(
                src_file.filepath
            )
            dest_blob_client = self.container_client.get_blob_client(dest_file.filepath)

            source_url = (
                f"{source_blob_client.url}?{self.config.credential.signature}"
                if isinstance(self.config.credential, AzureSasCredential)
                else source_blob_client.url
            )

            dest_blob_client.start_copy_from_url(source_url)
            source_blob_client.delete_blob()

    def delete_files(self, filepaths: list[FileSystemObject]) -> None:
        assert self.service_client is not None and self.container_client is not None, (
            "call to delete_files on uninitialized blob session"
        )
        for file_object in filepaths:
            if not isinstance(file_object, FileSystemFileReference):
                raise IncompatibleFileReference()

            blob_client = self.container_client.get_blob_client(file_object.filepath)
            blob_client.delete_blob()
