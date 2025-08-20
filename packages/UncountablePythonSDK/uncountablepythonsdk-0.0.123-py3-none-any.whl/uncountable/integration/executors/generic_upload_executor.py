import datetime
import io
import os
import re
from datetime import UTC

import paramiko

from pkgs.filesystem_utils import (
    FileObjectData,
    FileSystemFileReference,
    FileSystemObject,
    FileSystemS3Config,
    FileSystemSession,
    FileSystemSFTPConfig,
    FileTransfer,
    S3Session,
    SFTPSession,
)
from uncountable.core.file_upload import DataFileUpload, FileUpload
from uncountable.integration.job import Job, JobArguments
from uncountable.integration.secret_retrieval import retrieve_secret
from uncountable.integration.telemetry import JobLogger
from uncountable.types.generic_upload_t import (
    GenericRemoteDirectoryScope,
    GenericUploadStrategy,
)
from uncountable.types.job_definition_t import (
    GenericUploadDataSource,
    GenericUploadDataSourceS3,
    GenericUploadDataSourceSFTP,
    JobResult,
    S3CloudProvider,
)


def _get_extension(filename: str) -> str | None:
    _, ext = os.path.splitext(filename)
    return ext.strip().lower()


def _run_keyword_detection(data: io.BytesIO, keyword: str) -> bool:
    try:
        text = io.TextIOWrapper(data)
        for line in text:
            if (
                keyword in line
                or re.search(keyword, line, flags=re.IGNORECASE) is not None
            ):
                return True
        return False
    except re.error:
        return False
    except UnicodeError:
        return False


def _filter_files_by_keyword(
    remote_directory: GenericRemoteDirectoryScope,
    files: list[FileObjectData],
    logger: JobLogger,
) -> list[FileObjectData]:
    if remote_directory.detection_keyword is None:
        return files

    filtered_files = []

    for file in files:
        extension = _get_extension(file.filename)

        if extension not in (".txt", ".csv"):
            raise NotImplementedError(
                "keyword detection is only supported for csv, txt files"
            )

        if _run_keyword_detection(file.file_IO, remote_directory.detection_keyword):
            filtered_files.append(file)

    return filtered_files


def _filter_by_filename(
    remote_directory: GenericRemoteDirectoryScope, files: list[FileSystemObject]
) -> list[FileSystemObject]:
    if remote_directory.filename_regex is None:
        return files

    return [
        file
        for file in files
        if file.filename is not None
        and re.search(remote_directory.filename_regex, file.filename)
    ]


def _filter_by_file_extension(
    remote_directory: GenericRemoteDirectoryScope, files: list[FileSystemObject]
) -> list[FileSystemObject]:
    if remote_directory.valid_file_extensions is None:
        return files

    return [
        file
        for file in files
        if file.filename is not None
        and os.path.splitext(file.filename)[-1]
        in remote_directory.valid_file_extensions
    ]


def _filter_by_max_files(
    remote_directory: GenericRemoteDirectoryScope, files: list[FileSystemObject]
) -> list[FileSystemObject]:
    if remote_directory.max_files is None:
        return files

    return files[: remote_directory.max_files]


def _pull_remote_directory_data(
    *,
    filesystem_session: FileSystemSession,
    remote_directory: GenericRemoteDirectoryScope,
    logger: JobLogger,
) -> list[FileObjectData]:
    files_to_pull = filesystem_session.list_files(
        dir_path=FileSystemFileReference(
            filepath=remote_directory.src_path,
        ),
        recursive=remote_directory.recursive,
    )
    logger.log_info(
        f"Pulled the following files {files_to_pull} from the remote directory {remote_directory}.",
    )

    files_to_pull = _filter_by_file_extension(remote_directory, files_to_pull)
    files_to_pull = _filter_by_filename(remote_directory, files_to_pull)
    files_to_pull = _filter_by_max_files(remote_directory, files_to_pull)

    logger.log_info(
        f"Accessing SFTP directory: {remote_directory.src_path} and pulling files: {', '.join([f.filename for f in files_to_pull if f.filename is not None])}",
    )
    return filesystem_session.download_files(files_to_pull)


def _filter_downloaded_file_data(
    remote_directory: GenericRemoteDirectoryScope,
    pulled_file_data: list[FileObjectData],
    logger: JobLogger,
) -> list[FileObjectData]:
    filtered_file_data = _filter_files_by_keyword(
        remote_directory=remote_directory, files=pulled_file_data, logger=logger
    )
    return filtered_file_data


def _move_files_post_upload(
    *,
    filesystem_session: FileSystemSession,
    remote_directory_scope: GenericRemoteDirectoryScope,
    success_file_paths: list[str],
    failed_file_paths: list[str],
) -> None:
    success_file_transfers: list[FileTransfer] = []
    appended_text = ""

    if remote_directory_scope.prepend_date_on_archive:
        appended_text = f"-{datetime.datetime.now(UTC).timestamp()}"

    for file_path in success_file_paths:
        filename = os.path.split(file_path)[-1]
        root, extension = os.path.splitext(filename)
        new_filename = f"{root}{appended_text}{extension}"
        # format is source, dest in the tuple
        success_file_transfers.append((
            FileSystemFileReference(file_path),
            FileSystemFileReference(
                os.path.join(
                    remote_directory_scope.success_archive_path,
                    new_filename,
                )
            ),
        ))

    failed_file_transfers: list[FileTransfer] = []
    for file_path in failed_file_paths:
        filename = os.path.split(file_path)[-1]
        root, extension = os.path.splitext(filename)
        new_filename = f"{root}{appended_text}{extension}"
        failed_file_transfers.append((
            FileSystemFileReference(file_path),
            FileSystemFileReference(
                os.path.join(
                    remote_directory_scope.failure_archive_path,
                    new_filename,
                )
            ),
        ))

    filesystem_session.move_files([*success_file_transfers, *failed_file_transfers])


class GenericUploadJob(Job[None]):
    def __init__(
        self,
        data_source: GenericUploadDataSource,
        remote_directories: list[GenericRemoteDirectoryScope],
        upload_strategy: GenericUploadStrategy,
    ) -> None:
        super().__init__()
        self.remote_directories = remote_directories
        self.upload_strategy = upload_strategy
        self.data_source = data_source

    @property
    def payload_type(self) -> type[None]:
        return type(None)

    def _construct_filesystem_session(self, args: JobArguments) -> FileSystemSession:
        match self.data_source:
            case GenericUploadDataSourceSFTP():
                if self.data_source.pem_secret is not None:
                    pem_secret = retrieve_secret(
                        self.data_source.pem_secret,
                        profile_metadata=args.profile_metadata,
                    )
                    pem_key = paramiko.RSAKey.from_private_key(io.StringIO(pem_secret))
                    sftp_config = FileSystemSFTPConfig(
                        ip=self.data_source.host,
                        username=self.data_source.username,
                        pem_path=None,
                        pem_key=pem_key,
                    )
                elif self.data_source.password_secret is not None:
                    password_secret = retrieve_secret(
                        self.data_source.password_secret,
                        profile_metadata=args.profile_metadata,
                    )
                    sftp_config = FileSystemSFTPConfig(
                        ip=self.data_source.host,
                        username=self.data_source.username,
                        pem_path=None,
                        password=password_secret,
                    )
                else:
                    raise ValueError(
                        "Either pem_secret or password_secret must be specified for sftp data source"
                    )
                return SFTPSession(sftp_config=sftp_config)
            case GenericUploadDataSourceS3():
                if self.data_source.access_key_secret is not None:
                    secret_access_key = retrieve_secret(
                        self.data_source.access_key_secret,
                        profile_metadata=args.profile_metadata,
                    )
                else:
                    secret_access_key = None

                if self.data_source.endpoint_url is None:
                    assert self.data_source.cloud_provider is not None, (
                        "either cloud_provider or endpoint_url must be specified"
                    )
                    match self.data_source.cloud_provider:
                        case S3CloudProvider.AWS:
                            endpoint_url = "https://s3.amazonaws.com"
                        case S3CloudProvider.OVH:
                            assert self.data_source.region_name is not None, (
                                "region_name must be specified for cloud_provider OVH"
                            )
                            endpoint_url = f"https://s3.{self.data_source.region_name}.cloud.ovh.net"
                else:
                    endpoint_url = self.data_source.endpoint_url

                s3_config = FileSystemS3Config(
                    endpoint_url=endpoint_url,
                    bucket_name=self.data_source.bucket_name,
                    region_name=self.data_source.region_name,
                    access_key_id=self.data_source.access_key_id,
                    secret_access_key=secret_access_key,
                    session_token=None,
                )

                return S3Session(s3_config=s3_config)

    def run_outer(self, args: JobArguments) -> JobResult:
        client = args.client
        batch_processor = args.batch_processor
        logger = args.logger

        with self._construct_filesystem_session(args) as filesystem_session:
            files_to_upload: list[FileUpload] = []
            for remote_directory in self.remote_directories:
                pulled_file_data = _pull_remote_directory_data(
                    filesystem_session=filesystem_session,
                    remote_directory=remote_directory,
                    logger=logger,
                )
                filtered_file_data = _filter_downloaded_file_data(
                    remote_directory=remote_directory,
                    pulled_file_data=pulled_file_data,
                    logger=args.logger,
                )
                for file_data in filtered_file_data:
                    files_to_upload.append(
                        DataFileUpload(
                            data=io.BytesIO(file_data.file_data),
                            name=file_data.filename,
                        )
                    )
                if not self.upload_strategy.skip_moving_files:
                    _move_files_post_upload(
                        filesystem_session=filesystem_session,
                        remote_directory_scope=remote_directory,
                        success_file_paths=[
                            file.filepath
                            if file.filepath is not None
                            else file.filename
                            for file in filtered_file_data
                        ],
                        # IMPROVE: use triggers/webhooks to mark failed files as failed
                        failed_file_paths=[],
                    )

            uploaded_files = client.upload_files(file_uploads=files_to_upload)

        file_ids = [file.file_id for file in uploaded_files]

        for destination in self.upload_strategy.destinations:
            for file_id in file_ids:
                batch_processor.invoke_uploader(
                    file_id=file_id,
                    uploader_key=self.upload_strategy.uploader_key,
                    destination=destination,
                )

        return JobResult(success=True)
