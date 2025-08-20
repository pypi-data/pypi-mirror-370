import os

from uncountable.core import (
    AsyncBatchProcessor,
    AuthDetailsApiKey,
    Client,
    MediaFileUpload,
)
from uncountable.types import recipe_metadata_t
from uncountable.types.identifier_t import IdentifierKeyBatchReference

client = Client(
    base_url="http://localhost:5000",
    auth_details=AuthDetailsApiKey(
        api_id=os.environ["UNC_API_ID"],
        api_secret_key=os.environ["UNC_API_SECRET_KEY"],
    ),
)
uploaded_file = client.upload_files(
    file_uploads=[
        MediaFileUpload(path="Downloads/my_file_to_upload.csv"),
    ]
)[0]

batch_processor = AsyncBatchProcessor(client=client)

recipe_batch_identifier = batch_processor.create_recipe(
    material_family_id=1, workflow_id=1
).batch_reference

batch_processor.set_recipe_metadata(
    recipe_key=IdentifierKeyBatchReference(reference=recipe_batch_identifier),
    recipe_metadata=[
        recipe_metadata_t.MetadataValue(
            metadata_id=102, value_file_ids=[uploaded_file.file_id]
        )
    ],
)

batch_processor.send()
