from io import BytesIO

from boto3.session import Session
from mypy_boto3_s3.service_resource import Bucket

from pkgs.filesystem_utils.file_type_utils import (
    FileObjectData,
    FileSystemFileReference,
    FileSystemObject,
    FileSystemS3Config,
    FileTransfer,
    IncompatibleFileReference,
)

from .filesystem_session import FileSystemSession


def _add_slash(prefix: str) -> str:
    if len(prefix) > 0 and prefix[-1] != "/":
        prefix = prefix + "/"
    return prefix


class S3Session(FileSystemSession):
    config: FileSystemS3Config

    def __init__(self, s3_config: FileSystemS3Config) -> None:
        super().__init__()
        self.config = s3_config

    def start(self) -> None:
        session = Session(region_name=self.config.region_name)
        s3_resource = session.resource(
            service_name="s3",
            endpoint_url=self.config.endpoint_url,
            aws_access_key_id=self.config.access_key_id,
            aws_secret_access_key=self.config.secret_access_key,
            aws_session_token=self.config.session_token,
        )

        self.bucket: Bucket | None = s3_resource.Bucket(self.config.bucket_name)

    def __enter__(self) -> "S3Session":
        self.start()
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.bucket = None

    def list_files(
        self,
        dir_path: FileSystemObject,
        *,
        recursive: bool = False,
        valid_extensions: list[str] | None = None,
    ) -> list[FileSystemObject]:
        if not isinstance(dir_path, FileSystemFileReference):
            raise IncompatibleFileReference()

        assert self.bucket is not None, "call to list_files on uninitialized s3 session"

        filesystem_references: list[FileSystemObject] = []
        prefix = _add_slash(dir_path.filepath)
        for obj in self.bucket.objects.filter(Prefix=prefix):
            if not recursive and (obj.key == prefix or "/" in obj.key[len(prefix) :]):
                continue
            if valid_extensions is None or any(
                obj.key.endswith(valid_extension)
                for valid_extension in valid_extensions
            ):
                filesystem_references.append(FileSystemFileReference(obj.key))

        return filesystem_references

    def download_files(
        self,
        filepaths: list[FileSystemObject],
    ) -> list[FileObjectData]:
        downloaded_files: list[FileObjectData] = []
        assert self.bucket is not None, (
            "call to download_files on uninitialized s3 session"
        )

        for file_object in filepaths:
            if (
                not isinstance(file_object, FileSystemFileReference)
                or file_object.filename is None
            ):
                raise IncompatibleFileReference()
            s3_file_obj = self.bucket.Object(file_object.filepath)
            response = s3_file_obj.get()
            file_obj_bytes = response["Body"].read()
            downloaded_files.append(
                FileObjectData(
                    file_data=file_obj_bytes,
                    file_IO=BytesIO(file_obj_bytes),
                    filename=file_object.filename,
                    filepath=file_object.filepath,
                )
            )

        return downloaded_files

    def move_files(self, file_mappings: list[FileTransfer]) -> None:
        assert self.bucket is not None, "call to move_files on uninitialized s3 session"

        for src_file, dest_file in file_mappings:
            if not isinstance(src_file, FileSystemFileReference) or not isinstance(
                dest_file, FileSystemFileReference
            ):
                raise IncompatibleFileReference()
            self.bucket.Object(dest_file.filepath).copy_from(
                CopySource={
                    "Bucket": self.bucket.name,
                    "Key": src_file.filepath,
                }
            )
            self.bucket.Object(src_file.filepath).delete()
