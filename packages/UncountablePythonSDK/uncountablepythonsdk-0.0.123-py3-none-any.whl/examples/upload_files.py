import os
from pprint import pprint

from uncountable.core import AuthDetailsApiKey, Client, MediaFileUpload

client = Client(
    base_url="http://localhost:5000",
    auth_details=AuthDetailsApiKey(
        api_id=os.environ["UNC_API_ID"],
        api_secret_key=os.environ["UNC_API_SECRET_KEY"],
    ),
)
uploaded = client.upload_files(
    file_uploads=[
        MediaFileUpload(path="Downloads/file"),
    ]
)
pprint(uploaded)
