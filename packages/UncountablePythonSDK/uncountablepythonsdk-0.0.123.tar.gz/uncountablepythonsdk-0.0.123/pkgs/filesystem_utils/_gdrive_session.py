import os
from io import BytesIO
from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build as build_gdrive_connection
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from tqdm import tqdm

from pkgs.filesystem_utils.file_type_utils import (
    FileObjectData,
    FileSystemFileReference,
    FileSystemObject,
    FileTransfer,
    IncompatibleFileReference,
    RemoteObjectReference,
)

from .filesystem_session import FileSystemSession

# NOTE: google apis do not have static types
GDriveResource = Any


def download_gdrive_file(
    gdrive_connection: GDriveResource,
    file_id: str,
    filename: str,
    mime_type: str,
    *,
    verbose: bool = False,
) -> FileObjectData | None:
    if "folder" in mime_type:
        if verbose:
            print(f"{filename} is a folder and will not be downloaded.")
        return None
    elif "google-apps" in mime_type:
        # Handle google workspace doc
        if "spreadsheet" in mime_type:
            if verbose:
                print(f"{filename} is a Google Sheet, exporting.")
            file_request = gdrive_connection.files().export_media(
                fileId=file_id, mimeType="text/csv"
            )
            filename += ".csv"
        elif "document" in mime_type:
            if verbose:
                print(f"{filename} is a Google Doc, exporting.")
            file_request = gdrive_connection.files().export_media(
                fileId=file_id, mimeType="application/msword"
            )
            filename += ".doc"
        else:
            if verbose:
                print(f"{filename} is an unsupported google workspace filetype.")
                print(f"Skipping. mimeType: {mime_type}.")
            return None
    else:
        file_request = gdrive_connection.files().get_media(fileId=file_id)

    file_handler = BytesIO()
    downloader = MediaIoBaseDownload(file_handler, file_request)
    download_complete = False
    while not download_complete:
        _status, download_complete = downloader.next_chunk()

    file_handler.seek(0)
    file_data = file_handler.read()
    return FileObjectData(
        file_data=file_data,
        file_IO=BytesIO(file_data),
        filename=filename,
        filepath=file_id,
        metadata={"id": file_id},
        mime_type=mime_type,
    )


def list_gdrive_files(
    gdrive_connection: GDriveResource, gdrive_folder_id: str, *, recurse: bool = False
) -> list[dict[str, str]]:
    query = f"parents = '{gdrive_folder_id}'"
    print("Listing files", end="", flush=True)
    paginated_files_in_folder = [
        (
            gdrive_connection.files()
            .list(
                q=query,
                corpora="allDrives",
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
            )
            .execute()
        )
    ]
    while paginated_files_in_folder[-1].get("nextPageToken") is not None:
        print(".", end="", flush=True)
        paginated_files_in_folder.append(
            gdrive_connection.files()
            .list(
                q=query,
                corpora="allDrives",
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
                pageToken=paginated_files_in_folder[-1]["nextPageToken"],
            )
            .execute()
        )
    print()
    # Get available files: https://developers.google.com/drive/api/v3/manage-downloads#python
    files: list[dict[str, str]] = []
    for files_in_folder in paginated_files_in_folder:
        files.extend(files_in_folder.get("files", []))
    subfiles: list[dict[str, str]] = []
    if recurse:
        for file in files:
            if file["mimeType"] == "application/vnd.google-apps.folder":
                subfiles.extend(
                    list_gdrive_files(
                        gdrive_connection=gdrive_connection,
                        gdrive_folder_id=file["id"],
                        recurse=True,
                    )
                )
    return [*files, *subfiles]


def upload_file_gdrive(
    gdrive_connection: GDriveResource,
    src_file: BytesIO,
    mime_type: str,
    dest_folder_id: str,
    dest_filename: str,
) -> None:
    file_metadata = {"name": dest_filename, "parents": [dest_folder_id]}
    media = MediaIoBaseUpload(src_file, mimetype=mime_type)
    try:
        gdrive_connection.files().create(
            body=file_metadata, media_body=media, fields="id", supportsAllDrives=True
        ).execute()
    except HttpError:
        print("FileSystemObject Upload to GDrive Unsuccessful")


def move_gdrive_file(
    gdrive_connection: GDriveResource,
    src_file_id: str,
    dest_folder_id: str,
    *,
    dest_filename: str | None = None,
) -> None:
    # Retrieve the existing parents to remove
    file = (
        gdrive_connection.files()
        .get(fileId=src_file_id, fields="parents, name", supportsTeamDrives=True)
        .execute()
    )

    new_filename = file["name"]
    if dest_filename is not None:
        new_filename = dest_filename
    previous_parents = ",".join(file.get("parents"))
    metadata = {"name": new_filename}
    gdrive_connection.files().update(
        fileId=src_file_id, body=metadata, fields="name", supportsTeamDrives=True
    ).execute()
    gdrive_connection.files().update(
        fileId=src_file_id,
        addParents=dest_folder_id,
        removeParents=previous_parents,
        fields="id, parents",
        supportsTeamDrives=True,
    ).execute()


def delete_gdrive_file(gdrive_connection: GDriveResource, file_id: str) -> None:
    gdrive_connection.files().delete(fileId=file_id, supportsAllDrives=True).execute()


class GDriveSession(FileSystemSession):
    def __init__(self, service_account_json_path: str) -> None:
        super().__init__()
        self.service_account_json_path = service_account_json_path

    def start(self) -> None:
        credentials = service_account.Credentials.from_service_account_file(  # type: ignore[no-untyped-call]
            self.service_account_json_path
        )
        gdrive_connection = build_gdrive_connection(
            "drive", "v3", credentials=credentials
        )
        self.connection = gdrive_connection

    def list_files(
        self,
        dir_path: FileSystemObject,
        *,
        recursive: bool = False,
        valid_file_extensions: tuple[str, ...] | None = None,
    ) -> list[FileSystemObject]:
        if not isinstance(dir_path, RemoteObjectReference):
            raise IncompatibleFileReference(
                "Incompatible FileSystemObject to GDriveSession.list_files"
            )
        if not dir_path.is_dir:
            raise IncompatibleFileReference(
                "FileSystemObject does not reference a directory"
            )
        files = list_gdrive_files(self.connection, dir_path.file_id, recurse=recursive)
        gdrive_files: list[FileSystemObject] = []
        for file_context in files:
            if (
                valid_file_extensions is not None
                and os.path.splitext(file_context["name"])[1]
                not in valid_file_extensions
            ):
                continue
            gdrive_files.append(
                RemoteObjectReference(
                    file_id=file_context["id"],
                    mime_type=file_context["mimeType"],
                    filename=file_context["name"],
                )
            )
        return gdrive_files

    def delete_files(self, filepaths: list[FileSystemObject]) -> None:
        """Warning:
        Security account must have sufficient permissions to perform delete!
        https://developers.google.com/drive/api/v3/reference/files/delete?hl=en
        https://developers.google.com/drive/api/v3/ref-roles
        """
        for file_object in filepaths:
            if not isinstance(file_object, RemoteObjectReference):
                raise IncompatibleFileReference(
                    "Incompatible FileSystemObject provided to GDriveSession.delete_files"
                )
            delete_gdrive_file(self.connection, file_object.file_id)

    def move_files(self, file_mappings: list[FileTransfer]) -> None:
        for src_file, dest_file in file_mappings:
            if (
                isinstance(src_file, FileSystemFileReference)
                or not isinstance(dest_file, RemoteObjectReference)
                or not dest_file.is_dir
                or (isinstance(src_file, RemoteObjectReference) and src_file.is_dir)
            ):
                continue
            new_filename = dest_file.filename
            if isinstance(src_file, RemoteObjectReference):
                if new_filename is not None:
                    move_gdrive_file(
                        self.connection,
                        src_file.file_id,
                        dest_file.file_id,
                        dest_filename=new_filename,
                    )
                else:
                    move_gdrive_file(
                        self.connection, src_file.file_id, dest_file.file_id
                    )
            elif isinstance(src_file, FileObjectData):
                if src_file.mime_type is None:
                    raise IncompatibleFileReference(
                        "No mime_type present on source file data."
                    )
                new_filename = src_file.filename
                if dest_file.filename is not None:
                    new_filename = dest_file.filename
                upload_file_gdrive(
                    self.connection,
                    src_file.file_IO,
                    src_file.mime_type,
                    dest_file.file_id,
                    new_filename,
                )
            else:
                raise IncompatibleFileReference(
                    "Unrecognized file reference in FileTransfer object"
                )

    def download_files(self, filepaths: list[FileSystemObject]) -> list[FileObjectData]:
        downloaded_files: list[FileObjectData] = []
        print(f"Downloading {len(filepaths)} files")
        for file_object in tqdm(filepaths):
            if (
                not isinstance(file_object, RemoteObjectReference)
                or file_object.filename is None
            ):
                raise IncompatibleFileReference(
                    "Incompatible FileSystemObject included in filepaths"
                )
            downloaded_file = download_gdrive_file(
                self.connection,
                file_object.file_id,
                file_object.filename,
                file_object.mime_type,
            )
            if downloaded_file is not None:
                downloaded_files.append(downloaded_file)
        return downloaded_files

    def __enter__(self) -> "GDriveSession":
        self.start()
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.connection.close()
