import io

from main.base.types import value_spec_t

# we'll assume these functions actually belong in the emit_python code, thus do an import of privates for now
from ..emit_python import INDENT, LINT_HEADER, MODIFY_NOTICE, python_class_name
from ..util import encode_common_string


def _function_symbol_name(function: value_spec_t.Function) -> str:
    return f"function_{function.name}"


def emit_functions(functions: list[value_spec_t.Function]) -> str:
    """
    We don't have a general purpose dataclass constant emitter yet. This is written strictly
    for the types involved here. We do eventually need this though, to emit more complex
    constants from type_spec values. It would have to be general purpose though.
    """
    out = io.StringIO()

    out.write(
        f"""{MODIFY_NOTICE}
{LINT_HEADER}
import datetime
from typing import cast, Union

from decimal import Decimal

from main.base.types import value_spec_t, base_t

from .function_wrapper import ExtractorArgs, WrapArgs
"""
    )

    out.write("\n")

    for function in functions:
        out.write(MODIFY_NOTICE)
        out.write(_emit_function(function, ""))
        out.write("\n")
        out.write(_emit_function_wrapper(function))
        out.write("\n")

    out.write(MODIFY_NOTICE)
    out.write("all_functions = [\n")
    for function in functions:
        out.write(f"{INDENT}{_function_symbol_name(function)},\n")
    out.write("]\n")

    out.write(MODIFY_NOTICE)
    return out.getvalue()


def _emit_function_wrapper(function: value_spec_t.Function) -> str:
    out = io.StringIO()
    args_name = f"Args{python_class_name(function.name)}"
    out.write(f"class {args_name}(ExtractorArgs):\n")
    any_pass_null = False
    for index, argument in enumerate(function.arguments):
        if argument.extant == value_spec_t.ArgumentExtant.REPEAT:
            out.write(
                f"""{INDENT}def get_{argument.ref_name}_len(self) -> int:
{INDENT}{INDENT}return self._extract_len({index})

{INDENT}def get_{argument.ref_name}_at(self, at: int) -> base_t.ExtJsonValue:
{INDENT}{INDENT}return self._extract_at({index}, at)
"""
            )
        else:
            python_type = _emit_python_type(argument.type)
            if (
                argument.on_null == value_spec_t.OnNull.PASS
                or argument.extant == value_spec_t.ArgumentExtant.MISSING
            ):
                python_type += " | None"
                any_pass_null = True

            if python_type.startswith("base_t.ExtJsonValue"):
                return_statement = f"self._extract({index})"
            else:
                return_statement = f"cast({python_type}, self._extract({index}))"
            out.write(
                f"""{INDENT}def get_{argument.ref_name}(self) -> {python_type}:
{INDENT}{INDENT}return {return_statement}
"""
            )
        out.write("\n")

    python_return_type = _emit_python_type(function.return_value.type)
    if any_pass_null:
        python_return_type += " | None"
    out.write(
        f"""
wrap_{function.name} = WrapArgs[{args_name}, {python_return_type}](
{INDENT}function=function_{function.name},
{INDENT}args_type={args_name},
)

"""
    )

    return out.getvalue()


BASE_TYPE_NAME_MAP = {
    value_spec_t.BaseType.ANY: "base_t.ExtJsonValue",
    value_spec_t.BaseType.BOOLEAN: "bool",
    value_spec_t.BaseType.CONDITION: "bool",
    value_spec_t.BaseType.DATE: "datetime.date",
    value_spec_t.BaseType.DATETIME: "datetime.datetime",
    value_spec_t.BaseType.DECIMAL: "Decimal",
    value_spec_t.BaseType.DICT: "dict",
    value_spec_t.BaseType.INTEGER: "int",
    value_spec_t.BaseType.LIST: "list",
    value_spec_t.BaseType.NONE: "None",
    value_spec_t.BaseType.OPTIONAL: "Optional",
    value_spec_t.BaseType.STRING: "str",
    value_spec_t.BaseType.SYMBOL: "str",
    value_spec_t.BaseType.UNION: "Union",
}


def _emit_python_type(value_type: value_spec_t.ValueType) -> str:
    # IMPROVE: Ideally we'd find a way to translate into type_spec types, or load directly, and
    # rely on the other conversions. This might be requier to avoid duplication in emitting TypeScript code later
    out = io.StringIO()
    out.write(BASE_TYPE_NAME_MAP[value_type.base_type])
    if value_type.parameters is not None:
        out.write("[")
        out.write(
            ", ".join([
                _emit_python_type(parameter) for parameter in value_type.parameters
            ])
        )
        out.write("]")

    return out.getvalue()


def _emit_type(value_type: value_spec_t.ValueType, indent: str) -> str:
    out = io.StringIO()
    out.write("value_spec_t.ValueType(\n")
    sub_indent = indent + INDENT
    out.write(
        f"{sub_indent}base_type=value_spec_t.BaseType.{value_type.base_type.name},\n"
    )

    if value_type.parameters is not None:
        out.write(f"{sub_indent}parameters=[\n")
        for param_type in value_type.parameters:
            out.write(
                f"{sub_indent + INDENT}{_emit_type(param_type, sub_indent + INDENT)},\n"
            )
        out.write(f"{sub_indent}],\n")

    out.write(f"{indent})")

    return out.getvalue()


def _emit_function(function: value_spec_t.Function, indent: str) -> str:
    out = io.StringIO()

    sub_indent = indent + INDENT
    out.write(f"{_function_symbol_name(function)} = value_spec_t.Function(\n")
    out.write(f"{sub_indent}name={encode_common_string(function.name)},\n")
    out.write(
        f"{sub_indent}description={encode_common_string(function.description)},\n"
    )
    out.write(f"{sub_indent}brief={encode_common_string(function.brief)},\n")
    if function.draft:
        out.write(f"{sub_indent}draft={function.draft},\n")
    out.write(
        f"{sub_indent}return_value={_emit_function_return(function.return_value, sub_indent)},\n"
    )

    out.write(f"{sub_indent}arguments=[\n")
    for argument in function.arguments:
        out.write(
            f"{sub_indent + INDENT}{_emit_argument(argument, sub_indent + INDENT)},\n"
        )
    out.write(f"{sub_indent}],\n")

    out.write(f"{indent})\n\n")
    return out.getvalue()


def _emit_argument(argument: value_spec_t.FunctionArgument, indent: str) -> str:
    out = io.StringIO()

    sub_indent = indent + INDENT
    out.write("value_spec_t.FunctionArgument(\n")
    out.write(f"{sub_indent}ref_name={encode_common_string(argument.ref_name)},\n")
    out.write(f"{sub_indent}name={encode_common_string(argument.name)},\n")
    out.write(
        f"{sub_indent}description={encode_common_string(argument.description)},\n"
    )
    # Quick enum emit since we have only one such type here
    out.write(
        f"{sub_indent}on_null=value_spec_t.OnNull.{str(argument.on_null).upper()},\n"
    )
    out.write(
        f"{sub_indent}extant=value_spec_t.ArgumentExtant.{argument.extant.name},\n"
    )
    out.write(f"{sub_indent}type={_emit_type(argument.type, sub_indent)},\n")
    out.write(f"{indent})")

    return out.getvalue()


def _emit_function_return(
    return_value: value_spec_t.FunctionReturn, indent: str
) -> str:
    out = io.StringIO()

    sub_indent = indent + INDENT
    out.write("value_spec_t.FunctionReturn(\n")
    out.write(f"{sub_indent}type={_emit_type(return_value.type, sub_indent)},\n")
    out.write(
        f"{sub_indent}description={encode_common_string(return_value.description)},\n"
    )
    out.write(f"{indent})")

    return out.getvalue()
