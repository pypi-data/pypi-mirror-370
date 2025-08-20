import os
from pprint import pprint

from uncountable.core import AuthDetailsApiKey, Client
from uncountable.types import download_file_t, entity_t, identifier_t

client = Client(
    base_url="http://localhost:5000",
    auth_details=AuthDetailsApiKey(
        api_id=os.environ["UNC_API_ID"],
        api_secret_key=os.environ["UNC_API_SECRET_KEY"],
    ),
)

file_query = download_file_t.FileDownloadQueryEntityField(
    entity=entity_t.EntityIdentifier(
        type=entity_t.EntityType.LAB_REQUEST,
        identifier_key=identifier_t.IdentifierKeyId(id=2375),
    ),
    field_key=identifier_t.IdentifierKeyRefName(ref_name="attachments"),
)

downloaded = client.download_files(
    file_query=file_query,
)
pprint(downloaded)
