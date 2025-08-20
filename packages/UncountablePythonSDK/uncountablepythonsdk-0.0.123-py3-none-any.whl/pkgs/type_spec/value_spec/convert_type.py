from dataclasses import dataclass

from main.base.types import value_spec_t

from ..util import ParsedTypePath


@dataclass(kw_only=True, frozen=True)
class MappedType:
    base_type: value_spec_t.BaseType
    param_count: int = 0
    variable_param_count: bool = False


TYPE_MAP = {
    # These are meant to match the same type-names in type_spec for consistency, even if the
    # interpreation is slightly different in some cases
    "Boolean": MappedType(base_type=value_spec_t.BaseType.BOOLEAN),
    "Condition": MappedType(base_type=value_spec_t.BaseType.CONDITION),
    "Date": MappedType(base_type=value_spec_t.BaseType.DATE),
    "DateTime": MappedType(base_type=value_spec_t.BaseType.DATETIME),
    "Decimal": MappedType(base_type=value_spec_t.BaseType.DECIMAL),
    "Dict": MappedType(base_type=value_spec_t.BaseType.DICT, param_count=2),
    "Integer": MappedType(base_type=value_spec_t.BaseType.INTEGER),
    "List": MappedType(base_type=value_spec_t.BaseType.LIST, param_count=1),
    "Optional": MappedType(base_type=value_spec_t.BaseType.OPTIONAL, param_count=1),
    "String": MappedType(base_type=value_spec_t.BaseType.STRING),
    "Union": MappedType(
        base_type=value_spec_t.BaseType.UNION, variable_param_count=True
    ),
    # not part of type_spec's types now
    "Symbol": MappedType(base_type=value_spec_t.BaseType.SYMBOL),
    "Any": MappedType(base_type=value_spec_t.BaseType.ANY),
    "None": MappedType(base_type=value_spec_t.BaseType.NONE),
    "Tuple": MappedType(
        base_type=value_spec_t.BaseType.TUPLE, variable_param_count=True
    ),
    "Never": MappedType(base_type=value_spec_t.BaseType.NEVER),
}


def convert_to_value_spec_type(parsed: ParsedTypePath) -> value_spec_t.ValueType:
    assert len(parsed) == 1
    part = parsed[0]
    mapped = TYPE_MAP.get(part.name)
    if mapped is None:
        raise Exception(f"unknown-type:{part}")

    assert part.literal_value is None

    part_parameters = part.parameters or []
    assert mapped.variable_param_count or mapped.param_count == len(part_parameters)
    assert not mapped.variable_param_count or len(part_parameters) > 0

    parameters = (
        None
        if not mapped.variable_param_count and mapped.param_count == 0
        else [convert_to_value_spec_type(parameter) for parameter in part_parameters]
    )

    return value_spec_t.ValueType(base_type=mapped.base_type, parameters=parameters)

    # Our formatter was duplicating the previous line for an unknown reason, this comment blocks that


def convert_from_value_spec_type(
    base_type: value_spec_t.BaseType,
) -> str:
    for type_spec_type, mapped_type in TYPE_MAP.items():
        if (
            mapped_type.base_type == base_type
            and mapped_type.param_count == 0
            and mapped_type.variable_param_count is False
        ):
            return type_spec_type
    raise ValueError(f"invalid value spec type {base_type}")
