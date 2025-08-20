import json
import os
from dataclasses import dataclass
from typing import TypeVar, Union

import regex as re

T = TypeVar("T")


def rewrite_file(filename: str, content: str) -> bool:
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    if os.path.exists(filename):
        with open(filename, encoding="utf-8") as filein:
            old_content = filein.read()
            if content == old_content:
                return False

    with open(filename, "w", encoding="utf-8") as fileout:
        fileout.write(content)
    print(filename)
    return True


LiteralTypeValue = Union[str, bool]


@dataclass
class ParsedTypePart:
    name: str
    # An empty list is distinct from None
    parameters: list["ParsedTypePath"] | None = None
    literal_value: LiteralTypeValue | None = None


ParsedTypePath = list[ParsedTypePart]


@dataclass
class ConsumedParameter:
    part: ParsedTypePart
    at: int


def consume_parameter(
    bits: list[str],
    at: int,
) -> ConsumedParameter:
    if bits[at] != "'":
        return ConsumedParameter(at=at, part=ParsedTypePart(name=bits[at]))
    quote_stack: list[str] = []
    at += 1
    while at < len(bits):
        if bits[at] == "'":
            return ConsumedParameter(
                at=at,
                part=ParsedTypePart(
                    name="_StringLiteral",
                    literal_value="".join(quote_stack),
                ),
            )
        quote_stack.append(bits[at])
        at += 1
    raise Exception("invalid-closing-token")


def parse_type_str(type_str: str) -> ParsedTypePath:
    """
    IMPROVE: will not detect all errors yet, focuses on correct cases
    """
    raw_bits: list[str] = re.split(r"([.<>,'])", type_str)
    bits = [
        stripped_bit
        for stripped_bit in (padded_bit.strip() for padded_bit in raw_bits)
        if stripped_bit != ""
    ]
    assert len(bits) > 0
    result: ParsedTypePath = []

    cur_part = ParsedTypePart(name=bits[0])
    cur_path = result
    cur_path.append(cur_part)

    path_stack: list[ParsedTypePath] = []

    at = 1
    while at < len(bits):
        c = bits[at]
        at += 1

        if c == "<" or c == ",":
            if c == "<":
                cur_part.parameters = []
                path_stack.append(cur_path)

            consumption = consume_parameter(bits, at)
            at = consumption.at
            cur_part = consumption.part

            cur_path = [cur_part]

            # IMPROVE: messy
            prec_part = path_stack[-1][-1]
            assert prec_part is not None and prec_part.parameters is not None
            prec_part.parameters.append(cur_path)
            at += 1

        elif c == ">":
            if len(path_stack) < 1:
                raise Exception("invalid-closing-token")
            cur_path = path_stack[-1]
            cur_part = cur_path[-1]
            path_stack.pop()

        elif c == ".":
            cur_part = ParsedTypePart(name=bits[at])
            cur_path.append(cur_part)
            at += 1

        else:
            raise Exception("invalid-token")

    if len(path_stack) > 0:
        raise Exception("unclosed-token")

    return result


def format_parsed_type(pts: ParsedTypePath) -> str:
    out = ""
    first = True
    for pt in pts:
        if not first:
            out += "."
        first = False
        out += pt.name

        if pt.parameters is not None:
            out += "<"
            out += ",".join([format_parsed_type(x) for x in pt.parameters])
            out += ">"

    return out


re_pattern_type_name = re.compile(r"^[A-Z][A-Za-z0-9]+$")
re_pattern_property_name = re.compile(r"^[a-z][a-z0-9_]*$")
re_pattern_split_name = re.compile(r"([\p{Lu}][^\p{Lu}]*|_)")


def is_valid_type_name(name: str) -> bool:
    return re_pattern_type_name.match(name) is not None


def is_valid_property_name(name: str) -> bool:
    return re_pattern_property_name.match(name) is not None


def check_fields(data: dict[str, T], allowed: list[str]) -> None:
    for key in data:
        if key not in allowed:
            raise Exception(f"unexpected-field: {key}. Allowed: {allowed}")


def split_any_name(name: str) -> list[str]:
    """
    Splits a name on case and underscores.
    myName => [my, name]
    my_name => [my, name]
    """
    bits: list[str] = re_pattern_split_name.split(name)
    return [s.lower() for s in filter(lambda x: x is not None and x != "_", bits)]


def encode_common_string(value: str) -> str:
    """
    Common language encoding of strings to escape special values
    """
    rep = json.dumps(value, ensure_ascii=True)
    return rep


def unused(_arg: T) -> None:
    """
    Identifies that an argument is intended not be used, as opposed to
    simply forgotten, or a remnant. This can happen in patterned calls
    where some arguments are superfluous.
    """
