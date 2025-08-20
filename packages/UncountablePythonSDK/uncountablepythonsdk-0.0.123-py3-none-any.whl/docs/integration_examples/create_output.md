# Create an Output

Use the `create_or_update_entity` method to create Outputs.

The following fields are required when creating an Output:
- `name`: The name of the Output
- `core_output_unitsId`: The unit the output is measured in
- `core_output_outputMaterialFamilies`: The list of material families in which to include the Output
- `core_output_quantityType`: The quantity type of the output

The reference name of the default definition of Ingredients is `unc_output_definition`

This is an example of a minimal output creation call

```{code-block} python
from uncountable.types import entity_t, field_values_t, identifier_t

client.create_or_update_entity(
    entity_type=entity_t.EntityType.OUTPUT,
    definition_key=identifier_t.IdentifierKeyRefName(ref_name="unc_output_definition"),
    field_values=[
        field_values_t.FieldArgumentValue(
            field_key=identifier_t.IdentifierKeyRefName(ref_name="name"),
            value=field_values_t.FieldValueText(value="Example Output"),
        ),
        field_values_t.FieldArgumentValue(
            field_key=identifier_t.IdentifierKeyRefName(ref_name="core_output_unitsId"),
            value=field_values_t.FieldValueId(
                entity_type=entity_t.EntityType.UNITS,
                identifier_key=identifier_t.IdentifierKeyId(id=1),
            ),
        ),
        field_values_t.FieldArgumentValue(
            field_key=identifier_t.IdentifierKeyRefName(
                ref_name="core_output_outputMaterialFamilies"
            ),
            value=field_values_t.FieldValueIds(
                entity_type=entity_t.EntityType.MATERIAL_FAMILY,
                identifier_keys=[identifier_t.IdentifierKeyId(id=1)],
            ),
        ),
        field_values_t.FieldArgumentValue(
            field_key=identifier_t.IdentifierKeyRefName(
                ref_name="core_output_quantityType"
            ),
            value=field_values_t.FieldValueFieldOption(value="numeric"),
        ),
    ],
)
```

Example Response:

```{code}
Data(modification_made=True, result_id=653, entity=None, result_values=None)
```
