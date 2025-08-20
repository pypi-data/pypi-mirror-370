from . import builder
from .emit_typescript_util import (
    INDENT,
    MODIFY_NOTICE,
    EmitTypescriptContext,
    resolve_namespace_ref,
    ts_name,
)

base_name_map_io_ts = {
    builder.BaseTypeName.s_boolean: "IO.boolean",
    builder.BaseTypeName.s_date: "IO.string",  # IMPROVE: Aliased DateStr
    builder.BaseTypeName.s_date_time: "IO.string",  # IMPROVE: encoded DateTimeStr
    # Decimal's are marked as to_string_values thus are strings in the front-end
    builder.BaseTypeName.s_decimal: "IO.string",
    builder.BaseTypeName.s_dict: "IO.Record<IO.unknown, IO.unknown>",
    builder.BaseTypeName.s_integer: "IO.number",
    builder.BaseTypeName.s_lossy_decimal: "IO.number",
    builder.BaseTypeName.s_opaque_key: "IO.string",
    builder.BaseTypeName.s_string: "IO.string",
    # UNC: global types
    builder.BaseTypeName.s_json_value: "IO.unknown",
}


def emit_type_io_ts(
    ctx: EmitTypescriptContext, stype: builder.SpecType, derive_types: bool
) -> None:
    _emit_type_io_ts_impl(ctx, stype)

    if derive_types:
        ctx.out.write(f"export type {stype.name} = IO.TypeOf<typeof IO{stype.name}>;")


def _emit_type_io_ts_impl(ctx: EmitTypescriptContext, stype: builder.SpecType) -> None:
    if not isinstance(stype, builder.SpecTypeDefn):
        return

    if stype.is_base or stype.is_predefined:
        return

    ctx.out.write("\n")
    ctx.out.write(MODIFY_NOTICE)

    if isinstance(stype, builder.SpecTypeDefnExternal):
        raise NotImplementedError()

    assert stype.is_exported, "expecting exported names"
    if isinstance(stype, builder.SpecTypeDefnAlias):
        raise NotImplementedError()

    if isinstance(stype, builder.SpecTypeDefnStringEnum):
        ctx.out.write(f"export const IO{stype.name} = IO.union([\n")
        assert stype.values
        for value in stype.values.values():
            ctx.out.write(f'{INDENT}IO.literal("{value}"),\n')
        ctx.out.write("])\n")
        return

    assert isinstance(stype, builder.SpecTypeDefnObject)
    assert stype.base is not None

    # base_type = ""
    if not stype.base.is_base:
        raise NotImplementedError()

    if stype.properties is not None:
        required_lines = []
        missable_lines = []
        for prop in stype.properties.values():
            ref_type = refer_to_io_ts(ctx, prop.spec_type)
            prop_name = ts_name(prop.name, stype.name_case)
            if prop.extant == builder.PropertyExtant.missing:
                # Unlike optional below, missing does not imply null is possible. They
                # treated distinctly.
                missable_lines.append(
                    f"{INDENT}{prop_name}: IO.union([{ref_type}, IO.undefined]),\n"
                )
            elif prop.extant == builder.PropertyExtant.optional:
                # Need to add in |null since Python side can produce null's right now
                # IMPROVE: It would be better if the serializer could instead omit the None's
                # Dropping the null should be forward compatible
                missable_lines.append(
                    f"{INDENT}{prop_name}: IO.union([{ref_type}, IO.null, IO.undefined]),\n"
                )
            else:
                required_lines.append(f"{INDENT}{prop_name}: {ref_type},\n")

        ctx.out.write(f"export const IO{stype.name} = ")
        if len(required_lines) == 0:
            ctx.out.write("IO.partial({\n")
            for line in missable_lines:
                ctx.out.write(line)
            ctx.out.write("})\n")
        elif len(missable_lines) == 0:
            ctx.out.write("IO.type({\n")
            for line in required_lines:
                ctx.out.write(line)
            ctx.out.write("})\n")
        else:
            assert len(missable_lines) > 0 and len(required_lines) > 0
            ctx.out.write("IO.intersection([\n")
            ctx.out.write(f"{INDENT}IO.partial({'{'}\n")
            for line in missable_lines:
                ctx.out.write(f"{INDENT}{line}")
            ctx.out.write(f"{INDENT}{'}'}),\n")
            ctx.out.write(f"{INDENT}IO.type({'{'}\n")
            for line in required_lines:
                ctx.out.write(f"{INDENT}{line}")
            ctx.out.write(f"{INDENT}{'}'}),\n")
            ctx.out.write("])\n")

        ctx.out.write("\n")


def refer_to_io_ts(
    ctx: EmitTypescriptContext,
    stype: builder.SpecType,
) -> str:
    if isinstance(stype, builder.SpecTypeInstance):
        if (
            stype.defn_type.name == builder.BaseTypeName.s_list
            or stype.defn_type.name == builder.BaseTypeName.s_readonly_array
        ):
            spec = refer_to_io_ts(ctx, stype.parameters[0])
            return f"IO.array({spec})"
        if stype.defn_type.name == builder.BaseTypeName.s_union:
            return f"IO.union([{', '.join([refer_to_io_ts(ctx, p) for p in stype.parameters])}])"
        if stype.defn_type.name == builder.BaseTypeName.s_optional:
            return f"IO.optional({refer_to_io_ts(ctx, stype.parameters[0])})"
        if stype.defn_type.name == builder.BaseTypeName.s_tuple:
            return f"IO.tuple([{', '.join([refer_to_io_ts(ctx, p) for p in stype.parameters])}])"
        return refer_to_io_ts(ctx, stype.defn_type)

    assert isinstance(stype, builder.SpecTypeDefn)
    if stype.is_base:  # assume correct namespace
        if stype.name == builder.BaseTypeName.s_list:
            return "IO.array(IO.unknown)"  # TODO: generic type
        return base_name_map_io_ts[builder.BaseTypeName(stype.name)]

    if stype.namespace == ctx.namespace:
        return f"IO{stype.name}"

    ctx.namespaces.add(stype.namespace)
    return f"{resolve_namespace_ref(stype.namespace)}.IO{stype.name}"
