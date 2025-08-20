import os
from decimal import Decimal

from uncountable.core import AsyncBatchProcessor, AuthDetailsApiKey, Client
from uncountable.types import (
    edit_recipe_inputs_t,
    recipe_workflow_steps_t,
)
from uncountable.types.identifier import IdentifierKeyBatchReference, IdentifierKeyId
from uncountable.types.recipe_identifiers import (
    RecipeIdentifiers,
)
from uncountable.types.recipe_inputs import QuantityBasis

client = Client(
    base_url=os.environ["UNC_BASE_URL"],
    auth_details=AuthDetailsApiKey(
        api_id=os.environ["UNC_API_ID"], api_secret_key=os.environ["UNC_API_SECRET_KEY"]
    ),
)
batch_loader = AsyncBatchProcessor(client=client)
recipe_identifiers: RecipeIdentifiers = []
req = batch_loader.create_recipe(
    material_family_id=1, workflow_id=1, identifiers=recipe_identifiers
)
created_recipe_reference = req.batch_reference
edits: list[edit_recipe_inputs_t.RecipeInputEdit] = []
edits.append(
    edit_recipe_inputs_t.RecipeInputEditAddInput(
        quantity_basis=QuantityBasis.MASS,
        ingredient_key=IdentifierKeyId(id=1),
        value_numeric=Decimal("56.7"),
    )
)
edits.append(
    edit_recipe_inputs_t.RecipeInputEditChangeBasisViewed(
        quantity_basis=QuantityBasis.VOLUME, ingredient_key=IdentifierKeyId(id=1)
    )
)
edits.append(
    edit_recipe_inputs_t.RecipeInputEditAddInstructions(
        instructions="Mix for 3 minutes"
    )
)
batch_loader.edit_recipe_inputs(
    recipe_key=IdentifierKeyBatchReference(reference=created_recipe_reference),
    edits=edits,
    recipe_workflow_step_identifier=recipe_workflow_steps_t.RecipeWorkflowStepIdentifierDefault(),
)
job_id = batch_loader.send()
