import os

from uncountable.core import AuthDetailsApiKey, Client, MediaFileUpload
from uncountable.types import generic_upload_t
from uncountable.types.identifier_t import IdentifierKeyId

client = Client(
    base_url="http://localhost:5000",
    auth_details=AuthDetailsApiKey(
        api_id=os.environ["UNC_API_ID"],
        api_secret_key=os.environ["UNC_API_SECRET_KEY"],
    ),
)
uploaded_file = client.upload_files(
    file_uploads=[
        MediaFileUpload(path="~/Downloads/my_file_to_upload.csv"),
    ]
)[0]

client.invoke_uploader(
    file_id=uploaded_file.file_id,
    uploader_key=IdentifierKeyId(id=48),
    destination=generic_upload_t.UploadDestinationMaterialFamily(
        material_family_key=IdentifierKeyId(id=7)
    ),
)
