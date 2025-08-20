import functools
import re


@functools.lru_cache(maxsize=500000)
def snake_to_camel_case(o: str) -> str:
    tokens = o.split("_")
    if len(tokens) < 2:
        return o
    return "".join([part.title() if i > 0 else part for i, part in enumerate(tokens)])


def kebab_to_pascal_case(o: str) -> str:
    return "".join(item.title() for item in o.split("-"))


RE_1 = re.compile(r"(.)([A-Z][a-z]+)")
RE_2 = re.compile(r"([a-z0-9])([A-Z])")
SUB_REGEX = r"\1_\2"


@functools.lru_cache(maxsize=500000)
def camel_to_snake_case(o: str) -> str:
    return RE_2.sub(SUB_REGEX, RE_1.sub(SUB_REGEX, o)).lower()
