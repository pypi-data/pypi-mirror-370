"""
This emittier relies on the output of the type_spec type generation.
The justfile calls them in the expected order.
This allows the processing at this layer to use the generated types for ext_info.
"""

import argparse
import sys

from ..config import parse_yaml_config
from ..load_types import load_types
from .emit_type_info import emit_type_info, emit_type_info_python


def main() -> bool:
    parser = argparse.ArgumentParser(
        "type_spec", usage="python -m type_spec.type_info config_file.yaml"
    )
    parser.add_argument("config_file", type=str)
    args = parser.parse_args()

    config = parse_yaml_config(args.config_file)
    builder = load_types(config)
    if builder is None:
        return False

    assert config.typescript is not None
    emit_type_info(builder, config.typescript.type_info_output)
    if config.python.type_info_output is not None:
        emit_type_info_python(builder, config.python.type_info_output)

    return True


sys.exit(0 if main() else 1)
