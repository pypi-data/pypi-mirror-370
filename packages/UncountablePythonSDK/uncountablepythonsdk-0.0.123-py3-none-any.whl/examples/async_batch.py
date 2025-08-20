import os
from decimal import Decimal

from uncountable.core import AsyncBatchProcessor, AuthDetailsApiKey, Client
from uncountable.types import (
    recipe_metadata,
)
from uncountable.types.identifier import IdentifierKeyBatchReference
from uncountable.types.recipe_identifiers import (
    RecipeIdentifierEditableName,
    RecipeIdentifiers,
)

client = Client(
    base_url=os.environ["UNC_BASE_URL"],
    auth_details=AuthDetailsApiKey(
        api_id=os.environ["UNC_API_ID"], api_secret_key=os.environ["UNC_API_SECRET_KEY"]
    ),
)
batch_loader = AsyncBatchProcessor(client=client)
recipe_identifiers: RecipeIdentifiers = []
recipe_identifiers.append(
    RecipeIdentifierEditableName(editable_name="My recipe from API")
)
req = batch_loader.create_recipe(
    material_family_id=1, workflow_id=1, identifiers=recipe_identifiers
)
created_recipe_reference = req.batch_reference
batch_loader.set_recipe_metadata(
    recipe_key=IdentifierKeyBatchReference(reference=created_recipe_reference),
    recipe_metadata=[
        recipe_metadata.MetadataValue(metadata_id=7, value_numeric=Decimal(38))
    ],
)
job_id = batch_loader.send()
