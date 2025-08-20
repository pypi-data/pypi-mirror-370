"""
This processes the file value_spec/functions.yaml and emits value_spec/functions.py
Most of the values pass-through to the value_spec_t namespace types, but signature has a compact syntax.

# signature

The signature is a Python-like typed signature. Only value_spec.ValueTypes are supported.

One of the following can be specified on the name of a argument:
- `+`: This argument occurs one or more times. It must be the final argument. The type must be a List.
- `?`: This argument may be absent from the call. This is different than a type of Optional, which may still be required.

After that you can also specify a `!` indicating the argument may not be null.
If this is not specified, then a null input on this argument should produce a null output.
We prefer not to use `!` as we want to encourage null pass-through where possible.

If null is allowed as a legitimate value, such as in conditionals like `is_null`,
then `!usenull` must be specified, this distinguishes it from the pass-through case.
The accepted argument type must accept "None", it is not implied.
"""

import sys
from typing import TypeVar, cast

import regex as re

from main.base.types import base_t, value_spec_t
from pkgs.serialization import yaml

from ..util import parse_type_str, rewrite_file
from .convert_type import convert_to_value_spec_type
from .emit_python import emit_functions
from .types import ParsedFunctionArgument, ParsedFunctionSignature


class Source:
    def __init__(self, text: str) -> None:
        self._text = text
        self._at = 0

    def skip_space(self) -> None:
        while self._at < len(self._text):
            c = self._text[self._at]
            if c not in [" ", "\t"]:
                break
            self._at += 1

    def next_char(self, *, skip_space: bool = True) -> str:
        if skip_space:
            self.skip_space()
        # We won't check for length validity now, allowing normal exceptions to propagate. Not friendly, but it works for now
        c = self._text[self._at]
        self._at += 1
        return c

    def has_more(self) -> bool:
        return self._at < len(self._text)

    def match(self, expression: re.Pattern) -> re.Match | None:
        self.skip_space()
        m = expression.match(self._text, self._at)
        if m is not None:
            self._at = m.end()
        return m

    def extract_type(self) -> str:
        """
        This is a hacky function that works for our current purposes.
        It grabs a type-string at the current location, accounting for balanced type brackets,
        and stopping at the first comma. It may fail on several valid types, but none that we use.
        To do properly the parse_type_str we call would have to support linear scanning.
        """
        open_bracket = 0
        start = self._at
        while self.has_more():
            c = self._text[self._at]
            if c == "<":
                open_bracket += 1
            if c == ">":
                open_bracket -= 1
                if open_bracket < 0:
                    raise Exception("unexpected-closing-angle-bracket")
            if c in [",", ")"] and open_bracket == 0:
                break
            self._at += 1

        return self._text[start : self._at]


_re_argument_name = re.compile(r"([a-z_]+)(\?|\+)?(!|!usenull)?:")


def parse_function_signature(text: str) -> ParsedFunctionSignature:
    source = Source(text)
    c = source.next_char()
    if c != "(":
        raise Exception("expecting-open-paren")

    arguments = []
    while source.has_more():
        arg_group = source.match(_re_argument_name)
        if arg_group is None:
            raise Exception("expecting-argument-name")

        type_str = source.extract_type()
        ref_name = arg_group.group(1)
        # is_missing = arg_group.group(2) == "?"
        # is_repeating = arg_group.group(2) == "+"
        type_path = parse_type_str(type_str)

        match arg_group.group(3):
            case "!":
                on_null = value_spec_t.OnNull.DISALLOW
            case "!usenull":
                on_null = value_spec_t.OnNull.USE
            case _:
                on_null = value_spec_t.OnNull.PASS

        extant = value_spec_t.ArgumentExtant.REQUIRED
        extant_marker = arg_group.group(2)
        if extant_marker == "?":
            extant = value_spec_t.ArgumentExtant.MISSING
        elif extant_marker == "+":
            extant = value_spec_t.ArgumentExtant.REPEAT

        arguments.append(
            ParsedFunctionArgument(
                ref_name=ref_name,
                on_null=on_null,
                extant=extant,
                type_path=type_path,
            )
        )

        c = source.next_char()
        if c == ",":
            continue
        if c == ")":
            break

    c = source.next_char() + source.next_char(skip_space=False)
    if c != "->":
        raise Exception("expecting-return-value")
    return_type_path = parse_type_str(source.extract_type())

    return ParsedFunctionSignature(
        arguments=arguments,
        return_type_path=return_type_path,
    )


key_signature = "signature"
key_arguments = "arguments"
key_return = "return"
key_description = "description"
key_brief = "brief"
key_name = "name"
key_draft = "draft"


TypeT = TypeVar("TypeT")


class InvalidSpecException(Exception):
    pass


def main() -> None:
    #  IMPROVE: Move paths to config file
    with open(
        "main/unc/materials/shared/value_spec/functions.yaml", encoding="utf-8"
    ) as input:
        in_functions = yaml.safe_load(input)

    functions = []

    where: list[str] = []

    def get_where() -> str:
        return "/".join(where)

    # The yaml library appears to emit "any" types, but they should only be PureJsonValue types
    def get(node: base_t.PureJsonValue, key: str) -> base_t.PureJsonValue:
        if not isinstance(node, dict):
            raise Exception(f"invalid-node:{node}:{get_where()}")
        x = node.get(key)
        if x is None:
            raise Exception(f"missing-{key}:{get_where()}")
        return cast(base_t.PureJsonValue, x)

    def get_as(node: base_t.PureJsonValue, key: str, type_: type[TypeT]) -> TypeT:
        raw = get(node, key)
        assert isinstance(raw, type_)

        if type_ is str:
            # MYPY: can't see the type_ / raw / str type relationships, thus the casts
            return cast(TypeT, cast(str, raw).strip())
        return raw

    try:
        for ref_name, spec in in_functions.items():
            where.append(ref_name)
            where.append("signature")
            parsed = parse_function_signature(spec[key_signature])
            where.pop()

            arguments = []
            where.append("arguments")
            args_meta = get(spec, key_arguments)
            for in_argument in parsed.arguments:
                where.append(in_argument.ref_name)
                arg_meta = get(args_meta, in_argument.ref_name)
                arg_description = get_as(arg_meta, key_description, str)
                arg_name = get_as(arg_meta, key_name, str)

                arguments.append(
                    value_spec_t.FunctionArgument(
                        ref_name=in_argument.ref_name,
                        name=arg_name,
                        description=arg_description,
                        type=convert_to_value_spec_type(in_argument.type_path),
                        on_null=in_argument.on_null,
                        extant=in_argument.extant,
                    )
                )

                where.pop()

            where.pop()

            brief = get_as(spec, key_brief, str)
            description = get_as(spec, key_description, str)
            draft = (
                get_as(spec, key_draft, bool)
                if spec.get(key_draft) is not None
                else None
            )

            return_value = get(spec, key_return)
            where.append("return")
            return_description = get_as(return_value, key_description, str)
            where.pop()

            functions.append(
                value_spec_t.Function(
                    name=ref_name,
                    brief=brief,
                    description=description,
                    arguments=arguments,
                    return_value=value_spec_t.FunctionReturn(
                        type=convert_to_value_spec_type(parsed.return_type_path),
                        description=return_description,
                    ),
                    draft=draft,
                )
            )
            where.pop()
    except InvalidSpecException:
        sys.exit(1)

    except Exception as e:
        print("Exception at", get_where())
        raise e

    py_content = emit_functions(functions)
    rewrite_file("main/unc/materials/shared/value_spec/functions.py", py_content)
    sys.exit(0)


main()
