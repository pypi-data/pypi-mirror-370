import os
from pathlib import Path

import uncountable.types.api.recipes.set_recipe_output_file as set_recipe_output_file_t
from uncountable.core import AuthDetailsApiKey, Client, MediaFileUpload

client = Client(
    base_url="http://localhost:5000",
    auth_details=AuthDetailsApiKey(
        api_id=os.environ["UNC_API_ID"],
        api_secret_key=os.environ["UNC_API_SECRET_KEY"],
    ),
)
uploaded_file = client.upload_files(
    file_uploads=[
        MediaFileUpload(
            path=str((Path.home() / "Downloads" / "my_file_to_upload.csv").absolute())
        ),
    ]
)[0]

client.set_recipe_output_file(
    output_file_data=set_recipe_output_file_t.RecipeOutputFileValue(
        recipe_id=58070, output_id=148, file_id=uploaded_file.file_id, experiment_num=1
    )
)
