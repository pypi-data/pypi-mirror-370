import os
from collections.abc import Callable
from io import StringIO

from shelljob import fs

from pkgs.serialization import yaml

from .builder import SpecBuilder
from .config import Config
from .cross_output_links import CrossOutputPaths

ext_map = {
    ".ts": "typescript",
    ".py": "python",
}

_DOC_FILE_REFEX = ".*/docs/(examples|guides)/.*yaml"
_EXAMPLE_FILE_REGEX = ".*/docs/examples/.*yaml"
_GUIDE_FILE_REGEX = ".*/docs/guides/.*md"


def find_and_handle_files(
    *,
    root_folder: str,
    handler: Callable[[str, str], None],
    name_regex: str | None = None,
    not_name_regex: str | None = None,
    whole_name_regex: str | None = None,
    not_whole_name_regex: str | None = None,
) -> None:
    for file_name in fs.find(
        root_folder,
        name_regex=name_regex,
        not_name_regex=not_name_regex,
        whole_name_regex=whole_name_regex,
        not_whole_name_regex=not_whole_name_regex,
        relative=True,
    ):
        with open(os.path.join(root_folder, file_name), encoding="utf-8") as file:
            handler(file_name, file.read())


def load_types(config: Config) -> SpecBuilder | None:
    if config.typescript is not None and config.python is not None:
        cross_output_paths = CrossOutputPaths(
            python_types_output=config.python.types_output,
            typescript_types_output=config.typescript.types_output,
            typescript_routes_output_by_endpoint=config.typescript.endpoint_to_routes_output,
            typespec_files_input=config.type_spec_types,
            # IMPROVE not sure how to know which one is the correct one in emit_typescript
        )
    else:
        cross_output_paths = None

    builder = SpecBuilder(
        api_endpoints=config.api_endpoint,
        top_namespace=config.top_namespace,
        cross_output_paths=cross_output_paths,
    )

    def handle_builder_add(
        file_name: str, file_content: str, handler: Callable[[str, str, str], None]
    ) -> None:
        by_name, _ = os.path.splitext(file_name)
        name, ext = os.path.splitext(by_name)
        handler(ext_map[ext], name, file_content)

    def handle_builder_example_add(file_name: str, file_content: str) -> None:
        yaml_content = yaml.safe_load(StringIO(file_content))
        builder.add_example_file(yaml_content)

    def handle_builder_guide_add(file_name: str, file_content: str) -> None:
        builder.add_guide_file(file_content)

    for folder in config.type_spec_types:
        find_and_handle_files(
            root_folder=folder,
            name_regex=".*\\.(ts|py)\\.part",
            handler=lambda file_name, file_content: handle_builder_add(
                file_name, file_content, builder.add_part_file
            ),
        )

    for folder in config.type_spec_types:
        find_and_handle_files(
            root_folder=folder,
            name_regex=".*\\.(ts|py)\\.prepart",
            handler=lambda file_name, file_content: handle_builder_add(
                file_name, file_content, builder.add_prepart_file
            ),
        )

    def builder_prescan_file(file_name: str, file_content: str) -> None:
        name, _ = os.path.splitext(file_name)
        data = yaml.safe_load(file_content)
        # May be a placeholder file
        if data is None:
            data = {}
        try:
            builder.prescan(name.replace("/", "."), data)
        except Exception:
            print(f"Failure adding {file_name}")
            raise

    for folder in config.type_spec_types:
        find_and_handle_files(
            root_folder=folder,
            name_regex=".*\\.yaml",
            not_whole_name_regex=_DOC_FILE_REFEX,
            handler=builder_prescan_file,
        )

    if config.open_api is not None:
        for folder in config.type_spec_types:
            find_and_handle_files(
                root_folder=folder,
                whole_name_regex=_EXAMPLE_FILE_REGEX,
                handler=handle_builder_example_add,
            )

        for folder in config.type_spec_types:
            find_and_handle_files(
                root_folder=folder,
                whole_name_regex=_GUIDE_FILE_REGEX,
                handler=handle_builder_guide_add,
            )

    if not builder.process():
        return None

    return builder
