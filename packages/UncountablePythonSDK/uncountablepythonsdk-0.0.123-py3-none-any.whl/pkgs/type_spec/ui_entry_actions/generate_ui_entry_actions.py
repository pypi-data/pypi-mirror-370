import json
import re
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import assert_never

from main.base.types import (
    base_t,
    ui_entry_actions_t,
)
from pkgs.serialization_util import serialize_for_api
from pkgs.type_spec import emit_typescript_util
from pkgs.type_spec.builder import (
    BaseTypeName,
    NameCase,
    RawDict,
    SpecBuilder,
    SpecNamespace,
    SpecTypeDefnObject,
)
from pkgs.type_spec.config import Config
from pkgs.type_spec.load_types import load_types
from pkgs.type_spec.util import rewrite_file
from pkgs.type_spec.value_spec.convert_type import convert_from_value_spec_type

_INIT_ACTION_INDEX_TYPE_DATA = {
    "EntryActionInfo<InputT, OutputT>": {
        "type": BaseTypeName.s_object,
        "properties": {"inputs": {"type": "InputT"}, "outputs": {"type": "OutputT"}},
    }
}
_TYPES_ROOT = "unc_types"


@dataclass(kw_only=True)
class EntryActionTypeInfo:
    inputs_type: SpecTypeDefnObject
    outputs_type: SpecTypeDefnObject
    name: str


def ui_entry_variable_to_type_spec_type(
    variable: ui_entry_actions_t.UiEntryActionVariable,
) -> str:
    match variable:
        case ui_entry_actions_t.UiEntryActionVariableString():
            return BaseTypeName.s_string
        case ui_entry_actions_t.UiEntryActionVariableSingleEntity():
            return "ObjectId"
        case _:
            assert_never(variable)


def construct_inputs_type_data(
    vars: dict[str, ui_entry_actions_t.UiEntryActionVariable],
) -> RawDict:
    if len(vars) == 0:
        return {"type": BaseTypeName.s_object}
    properties: dict[str, dict[str, str]] = {}
    for input_name, input_defn in (vars).items():
        properties[f"{input_name}"] = {
            "type": ui_entry_variable_to_type_spec_type(input_defn)
        }
    return {"type": BaseTypeName.s_object, "properties": properties}


def construct_outputs_type_data(
    vars: dict[str, ui_entry_actions_t.UiEntryActionOutput],
) -> RawDict:
    if len(vars) == 0:
        return {"type": BaseTypeName.s_object}
    properties: dict[str, dict[str, str]] = {}
    for output_name, output_defn in (vars).items():
        # All outputs are optional
        properties[f"{output_name}"] = {
            "type": f"Optional<{convert_from_value_spec_type(output_defn.vs_type)}>"
        }
    return {"type": BaseTypeName.s_object, "properties": properties}


def construct_outputs_type(
    *,
    action_scope: ui_entry_actions_t.ActionScope,
    vars: dict[str, ui_entry_actions_t.UiEntryActionOutput],
    builder: SpecBuilder,
    namespace: SpecNamespace,
) -> SpecTypeDefnObject:
    stype = SpecTypeDefnObject(
        namespace=namespace,
        name=emit_typescript_util.ts_type_name(f"{action_scope}_outputs"),
    )
    namespace.types[stype.name] = stype
    stype.process(
        builder=builder,
        data=construct_outputs_type_data(vars=vars),
    )
    return stype


def construct_inputs_type(
    *,
    action_scope: ui_entry_actions_t.ActionScope,
    vars: dict[str, ui_entry_actions_t.UiEntryActionVariable],
    builder: SpecBuilder,
    namespace: SpecNamespace,
) -> SpecTypeDefnObject:
    stype = SpecTypeDefnObject(
        namespace=namespace,
        name=emit_typescript_util.ts_type_name(f"{action_scope}_inputs"),
    )
    stype.process(builder=builder, data=construct_inputs_type_data(vars))
    namespace.types[stype.name] = stype
    return stype


def _get_types_root(destination_root: Path) -> Path:
    return destination_root / "types"


def emit_imports_ts(
    namespaces: set[SpecNamespace],
    out: StringIO,
) -> None:
    for ns in sorted(
        namespaces,
        key=lambda ns: ns.name,
    ):
        import_as = emit_typescript_util.resolve_namespace_ref(ns)
        import_from = f"{_TYPES_ROOT}/{ns.name}"
        out.write(f'import * as {import_as} from "{import_from}"\n')


def emit_entry_action_definition(
    *,
    ctx: emit_typescript_util.EmitTypescriptContext,
    defn: ui_entry_actions_t.UiEntryActionDefinition,
    builder: SpecBuilder,
    action_scope: ui_entry_actions_t.ActionScope,
) -> EntryActionTypeInfo:
    inputs_type = construct_inputs_type(
        action_scope=action_scope,
        vars=defn.inputs,
        builder=builder,
        namespace=ctx.namespace,
    )
    outputs_type = construct_outputs_type(
        action_scope=action_scope,
        vars=defn.outputs,
        builder=builder,
        namespace=ctx.namespace,
    )

    return EntryActionTypeInfo(
        inputs_type=inputs_type,
        outputs_type=outputs_type,
        name=action_scope,
    )


def _validate_input(input: ui_entry_actions_t.UiEntryActionVariable) -> None:
    if "_" in input.vs_var_name:
        raise ValueError(f"Expected camelCase for variable {input.vs_var_name}")
    if not re.fullmatch(base_t.REF_NAME_STRICT_REGEX, input.vs_var_name):
        raise ValueError(
            f"Variable {input.vs_var_name} has invalid syntax. See REF_NAME_STRICT_REGEX"
        )


def emit_query_index(
    ctx: emit_typescript_util.EmitTypescriptContext,
    defn_infos: list[EntryActionTypeInfo],
    index_path: Path,
    builder: SpecBuilder,
    definitions: dict[
        ui_entry_actions_t.ActionScope, ui_entry_actions_t.UiEntryActionDefinition
    ],
) -> bool:
    query_index_type_data = {
        **_INIT_ACTION_INDEX_TYPE_DATA,
        "EntityActionTypeLookup": {
            "type": BaseTypeName.s_object,
            "properties": {
                defn_info.name: {
                    "type": f"EntryActionInfo<{defn_info.inputs_type.name},{defn_info.outputs_type.name}>",
                    "name_case": NameCase.preserve,
                }
                for defn_info in defn_infos
            },
        },
        "InputInfo": {
            "type": BaseTypeName.s_object,
            "properties": {
                "value_spec_var": {"type": "String"},
                "type": {"type": "ui_entry_actions.UiEntryActionDataType"},
                "variable": {"type": "ui_entry_actions.UiEntryActionVariable"},
            },
        },
        "OutputInfo": {
            "type": BaseTypeName.s_object,
            "properties": {
                "name": {"type": "String"},
                "desc": {"type": "String"},
                "type": {"type": "value_spec.BaseType"},
            },
        },
        "DefinitionInfo": {
            "type": BaseTypeName.s_object,
            "properties": {
                "inputs": {
                    "type": "ReadonlyArray<InputInfo>",
                },
                "outputs": {
                    "type": "ReadonlyArray<OutputInfo>",
                },
            },
        },
    }
    ctx.namespace.prescan(query_index_type_data)
    ctx.namespace.process(
        builder=builder,
        data=query_index_type_data,
    )

    defn_lookup_info = {}
    for scope, defn in definitions.items():
        inputs = []
        outputs = []
        for input in defn.inputs.values():
            _validate_input(input)
            inputs.append(
                serialize_for_api({
                    "value_spec_var": input.vs_var_name,
                    "type": input.type,
                    "variable": input,
                })
            )
        for name, output in defn.outputs.items():
            outputs.append(
                serialize_for_api({
                    "name": name,
                    "desc": output.description,
                    "type": output.vs_type,
                })
            )
        defn_lookup_info[scope] = {"inputs": inputs, "outputs": outputs}

    defn_lookup_out = f"export const DEFINITION_LOOKUP = {json.dumps(defn_lookup_info, sort_keys=True, indent=2)} as const\n\nexport const DEFINITION_LOOKUP_TYPED = DEFINITION_LOOKUP as Record<UiEntryActionsT.ActionScope, DefinitionInfo>\n"

    for stype in ctx.namespace.types.values():
        emit_typescript_util.emit_type_ts(
            ctx=ctx,
            stype=stype,
        )

    import_buffer = StringIO()
    emit_typescript_util.emit_namespace_imports_from_root_ts(
        namespaces=ctx.namespaces,
        out=import_buffer,
        root=_TYPES_ROOT,
    )

    return rewrite_file(
        content=import_buffer.getvalue() + ctx.out.getvalue() + defn_lookup_out,
        filename=str(index_path),
    )


def generate_entry_actions_typescript(
    *,
    definitions: dict[
        ui_entry_actions_t.ActionScope, ui_entry_actions_t.UiEntryActionDefinition
    ],
    destination_root: Path,
    materials_type_spec_config: Config,
) -> None:
    builder = load_types(materials_type_spec_config)
    assert builder is not None

    definition_buffer = StringIO()
    index_namespace = SpecNamespace(name="index")
    ctx = emit_typescript_util.EmitTypescriptContext(
        out=definition_buffer,
        namespace=index_namespace,
        api_endpoints={},
    )
    builder.namespaces[index_namespace.name] = index_namespace

    defn_infos: list[EntryActionTypeInfo] = []

    for action_scope, defn in definitions.items():
        defn_infos.append(
            emit_entry_action_definition(
                action_scope=action_scope,
                ctx=ctx,
                defn=defn,
                builder=builder,
            )
        )

    index_path = _get_types_root(destination_root) / "index.ts"
    emit_query_index(
        ctx=ctx,
        builder=builder,
        defn_infos=defn_infos,
        definitions=definitions,
        index_path=index_path,
    )
