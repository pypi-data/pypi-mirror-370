import os

import uncountable.types.api.inputs.create_inputs as create_inputs
from uncountable.core import AuthDetailsApiKey, Client
from uncountable.types import field_values_t, inputs_t

client = Client(
    base_url="http://localhost:5000",
    auth_details=AuthDetailsApiKey(
        api_id=os.environ["UNC_API_ID"],
        api_secret_key=os.environ["UNC_API_SECRET_KEY"],
    ),
)

client.external_create_inputs(
    inputs_to_create=[
        create_inputs.InputToCreate(
            name="sdk test ing",
            material_family_ids=[1],
            quantity_type=inputs_t.IngredientQuantityType.NUMERIC,
            type=inputs_t.IngredientType.INGREDIENT,
            field_values=[
                field_values_t.FieldRefNameValue(
                    field_ref_name="carrieTestNumericField",
                    value="10",
                ),
                field_values_t.FieldRefNameValue(
                    field_ref_name="carrieTestCheckboxField",
                    value=True,
                ),
            ],
        )
    ]
)
