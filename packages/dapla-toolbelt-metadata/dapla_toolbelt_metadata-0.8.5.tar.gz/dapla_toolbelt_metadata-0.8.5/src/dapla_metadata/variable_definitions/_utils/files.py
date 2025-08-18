"""Lower level file utilities."""

import logging
from datetime import datetime
from pathlib import Path

import pytz
from ruamel.yaml import YAML
from ruamel.yaml import CommentedMap
from ruamel.yaml import RoundTripRepresenter
from ruamel.yaml.scalarstring import DoubleQuotedScalarString
from ruamel.yaml.scalarstring import LiteralScalarString

from dapla_metadata.variable_definitions._generated.vardef_client.models.complete_response import (
    CompleteResponse,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.variable_status import (
    VariableStatus,
)
from dapla_metadata.variable_definitions._utils import config
from dapla_metadata.variable_definitions._utils.constants import BLOCK_FIELDS
from dapla_metadata.variable_definitions._utils.constants import DOUBLE_QUOTE_FIELDS
from dapla_metadata.variable_definitions._utils.constants import (
    MACHINE_GENERATED_FIELDS,
)
from dapla_metadata.variable_definitions._utils.constants import OWNER_FIELD_NAME
from dapla_metadata.variable_definitions._utils.constants import (
    TEMPLATE_SECTION_HEADER_MACHINE_GENERATED,
)
from dapla_metadata.variable_definitions._utils.constants import (
    TEMPLATE_SECTION_HEADER_OWNER,
)
from dapla_metadata.variable_definitions._utils.constants import (
    TEMPLATE_SECTION_HEADER_STATUS,
)
from dapla_metadata.variable_definitions._utils.constants import (
    VARIABLE_DEFINITIONS_DIR,
)
from dapla_metadata.variable_definitions._utils.constants import (
    VARIABLE_STATUS_FIELD_NAME,
)
from dapla_metadata.variable_definitions._utils.constants import YAML_STR_TAG
from dapla_metadata.variable_definitions.exceptions import VardefFileError

logger = logging.getLogger(__name__)


def _create_file_name(
    base_name: str,
    time_object: str,
    short_name: str | None = None,
    variable_definition_id: str | None = None,
) -> str:
    """Return file name with dynamic timestamp, and shortname and id if available."""
    return (
        "_".join(
            filter(
                None,
                [
                    base_name,
                    short_name,
                    variable_definition_id,
                    time_object,
                ],
            ),
        )
        + ".yaml"
    )


def _get_current_time() -> str:
    """Return a string format date now for filename."""
    timezone = pytz.timezone("Europe/Oslo")
    current_datetime = datetime.now(timezone).strftime("%Y-%m-%dT%H-%M-%S")
    return str(current_datetime)


def _get_workspace_dir() -> Path:
    """Determine the workspace directory."""
    workspace_dir = config.get_workspace_dir()

    if workspace_dir is None:
        msg = "WORKSPACE_DIR is not set. Check your configuration or provide a custom directory."
        raise VardefFileError(msg)
    workspace_dir_path: Path
    if workspace_dir is not None:
        workspace_dir_path = Path(workspace_dir)
        workspace_dir_path.resolve()

        if not workspace_dir_path.exists():
            msg = f"Directory '{workspace_dir_path}' does not exist."
            raise FileNotFoundError(msg)

        if not workspace_dir_path.is_dir():
            msg = f"'{workspace_dir_path}' is not a directory."
            raise NotADirectoryError(msg)
        logger.debug("'WORKSPACE_DIR' value: %s", workspace_dir)
    return workspace_dir_path


def _get_variable_definitions_dir():
    """Get or create the variable definitions directory inside the workspace."""
    workspace_dir = _get_workspace_dir()
    folder_path = workspace_dir / VARIABLE_DEFINITIONS_DIR
    folder_path.mkdir(parents=True, exist_ok=True)
    return folder_path


def _validate_and_create_directory(custom_directory: Path) -> Path:
    """Ensure that the given path is a valid directory, creating it if necessary.

    Args:
        custom_directory (Path): The target directory path.

    Returns:
        Path: The resolved absolute path of the directory.

    Raises:
        ValueError: If the provided path has a file suffix, indicating a file name instead of a directory.
        NotADirectoryError: If the path exists but is not a directory.
        PermissionError: If there are insufficient permissions to create the directory.
        OSError: If an OS-related error occurs while creating the directory.
    """
    custom_directory = Path(custom_directory).resolve()

    if custom_directory.suffix:
        msg = f"Expected a directory but got a file name: %{custom_directory.name}"
        raise ValueError(msg)

    if custom_directory.exists() and not custom_directory.is_dir():
        msg = f"Path exists but is not a directory: {custom_directory}"
        raise NotADirectoryError(msg)

    try:
        custom_directory.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        msg = f"Insufficient permissions to create directory: {custom_directory}"
        raise PermissionError(msg) from e
    except OSError as e:
        msg = f"Failed to create directory {custom_directory}: {e!s}"
        raise OSError(msg) from e

    return custom_directory


def configure_yaml(yaml: YAML) -> YAML:
    """Common Yaml config for variable definitions."""
    yaml.Representer = RoundTripRepresenter  # Preserve the order of keys etc.
    yaml.default_flow_style = False  # Ensures pretty YAML formatting block style
    yaml.allow_unicode = True  # Support special characters
    yaml.preserve_quotes = True
    yaml.width = 4096  # prevent wrapping lines
    yaml.indent(
        mapping=4,
        sequence=6,
        offset=4,
    )  # Ensure indentation for nested keys and lists
    yaml.representer.add_representer(
        VariableStatus,
        lambda dumper, data: dumper.represent_scalar(
            YAML_STR_TAG,
            data.value,
        ),
    )

    return yaml


def _safe_get(data: dict, keys: list):
    """Safely navigate nested dictionaries."""
    for key in keys:
        if not isinstance(data, dict) or key not in data or data[key] is None:
            return None
        data = data[key]
    return data


def _apply_literal_scalars(field: dict):
    """Helper function to wrap `LanguageStringType` values in `LiteralScalarString`.

    This function wraps each non-`None` language value in a `LanguageStringType` field
    in the `LiteralScalarString` YAML type, ensuring proper YAML formatting with block style.
    """
    for lang, value in field.items():
        if value is not None:
            field[lang] = LiteralScalarString(value)


def _apply_double_quotes_to_dict_values(field: dict):
    """Helper function to wrap dictionary values in `DoubleQuotedScalarString`.

    This function wraps each non-`None` value in a dictionary, including values inside lists,
    in the `DoubleQuotedScalarString` YAML type, ensuring proper YAML formatting with double quotes.
    """
    for sub_key, sub_value in field.items():
        if isinstance(sub_value, list):
            field[sub_key] = [
                DoubleQuotedScalarString(item) for item in sub_value if item is not None
            ]
        elif sub_value is not None:
            field[sub_key] = DoubleQuotedScalarString(sub_value)


def pre_process_data(data: dict) -> dict:
    """Format variable definition model fields with ruamel YAML scalar string types.

    This method sets the appropriate scalar string type (either `LiteralScalarString` or `DoubleQuotedScalarString`)
    for fields of the variable definition model, based on predefined lists of fields.

    It processes both nested dictionaries and lists, ensuring each element is formatted with the correct YAML string type.

    Args:
        data (dict): A dictionary containing the variable definition data.

    Returns:
        dict: The updated dictionary with model fields formatted as ruamel.yaml scalar string types.
    """
    for key in BLOCK_FIELDS:
        keys = key.split(".")
        field = _safe_get(data, keys)
        if isinstance(field, dict):
            _apply_literal_scalars(field)

    for key in DOUBLE_QUOTE_FIELDS:
        keys = key.split(".")
        field = _safe_get(data, keys)
        if isinstance(field, list):
            data[key] = [
                DoubleQuotedScalarString(item) for item in field if item is not None
            ]
        elif isinstance(field, str):
            data[key] = DoubleQuotedScalarString(data[key])
        elif isinstance(field, dict):
            _apply_double_quotes_to_dict_values(field)

    return data


def _model_to_yaml_with_comments(
    model_instance: CompleteResponse,
    file_name: str,
    start_comment: str,
    custom_directory: Path | None = None,
) -> Path:
    """Convert a model instance to a structured YAML file.

    Organizes fields into sections with headers and saves
    the YAML file with a structured format and timestamped filename.

    Args:
        model_instance: The model instance to convert.
        file_name: Name of the generated YAML file.
        start_comment: Comment at the top of the file.
        custom_directory: Optional directory to save the file.

    Returns:
        Path: The file path of the generated YAML file.
    """
    yaml = YAML()
    configure_yaml(yaml)

    # Convert Pydantic model instance to dictionary
    data = model_instance.model_dump(
        serialize_as_any=True,
        warnings="error",
    )
    data = pre_process_data(data)
    # One CommentMap for each section in the yaml file
    machine_generated_map = CommentedMap()
    commented_map = CommentedMap()
    status_map = CommentedMap()
    owner_map = CommentedMap()

    # Loop through all fields in the model and assigne to commented maps
    for field_name, value in data.items():
        if field_name == VARIABLE_STATUS_FIELD_NAME:
            status_map[field_name] = value
        elif field_name == OWNER_FIELD_NAME:
            owner_map[field_name] = value
        elif field_name in MACHINE_GENERATED_FIELDS:
            machine_generated_map[field_name] = value
        else:
            commented_map[field_name] = value

    base_path = (
        _get_variable_definitions_dir()
        if custom_directory is None
        else _validate_and_create_directory(custom_directory)
    )

    file_path = base_path / file_name

    # It is important to preserve the order of the yaml dump operations when writing to file
    # so that the file is predictable for the user
    with file_path.open("w", encoding="utf-8") as file:
        commented_map.yaml_set_start_comment(start_comment)
        yaml.dump(commented_map, file)

        status_map.yaml_set_start_comment(TEMPLATE_SECTION_HEADER_STATUS)
        yaml.dump(status_map, file)

        owner_map.yaml_set_start_comment(TEMPLATE_SECTION_HEADER_OWNER)
        yaml.dump(owner_map, file)

        machine_generated_map.yaml_set_start_comment(
            TEMPLATE_SECTION_HEADER_MACHINE_GENERATED,
        )
        yaml.dump(machine_generated_map, file)
    return file_path
