import argparse
import sys

from .config import parse_yaml_config
from .emit_open_api import emit_open_api
from .emit_python import emit_python
from .emit_typescript import emit_typescript
from .load_types import load_types


def main() -> bool:
    parser = argparse.ArgumentParser(
        "type_spec", usage="python -m type_spec config_file.yaml"
    )
    parser.add_argument("config_file", type=str)
    parser.add_argument("--docs", action="store_true")
    args = parser.parse_args()

    config = parse_yaml_config(args.config_file)
    builder = load_types(config)
    if builder is None:
        return False

    if args.docs:
        open_api_config = config.open_api
        assert open_api_config is not None, "missing open api config"
        emit_open_api(
            builder,
            config=open_api_config,
        )
    else:
        emit_python(builder, config=config.python)

        if config.typescript is not None:
            emit_typescript(builder, config.typescript)

    return True


sys.exit(0 if main() else 1)
