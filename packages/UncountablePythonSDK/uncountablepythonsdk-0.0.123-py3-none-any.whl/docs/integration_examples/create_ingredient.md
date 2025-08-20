# Create an Ingredient

Use the `create_or_update_entity` method to create Ingredients.

The following fields are required when creating an Ingredient:
- `name`: The name of the Ingredient
- `core_ingredient_ingredientMaterialFamilies`: The list of material families in which to include the Ingredient

The reference name of the default definition of Ingredients is `uncIngredient`

This is an example of a minimal ingredient creation call

```{code-block} python
from uncountable.types import entity_t, field_values_t, identifier_t

client.create_or_update_entity(
    entity_type=entity_t.EntityType.INGREDIENT,
    definition_key=identifier_t.IdentifierKeyRefName(ref_name="uncIngredient"),
    field_values=[
        field_values_t.FieldArgumentValue(
            field_key=identifier_t.IdentifierKeyRefName(
                ref_name="core_ingredient_ingredientMaterialFamilies"
            ),
            value=field_values_t.FieldValueIds(
                entity_type=entity_t.EntityType.MATERIAL_FAMILY,
                identifier_keys=[identifier_t.IdentifierKeyId(id=1)],
            ),
        ),
        field_values_t.FieldArgumentValue(
            field_key=identifier_t.IdentifierKeyRefName(ref_name="name"),
            value=field_values_t.FieldValueText(value="Example Ingredient"),
        ),
    ],
)
```

Example Response:
```{code}
Data(modification_made=True, result_id=3124, entity=None, result_values=None)
```

Optional fields:
- `core_ingredient_quantityType`: The quantity type of the ingredient (default is `numeric`)
