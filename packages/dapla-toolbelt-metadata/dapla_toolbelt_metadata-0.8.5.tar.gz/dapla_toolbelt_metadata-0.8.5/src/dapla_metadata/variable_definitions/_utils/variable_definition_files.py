"""Utilities for writing and reading existing variable definition files."""

import logging
from io import StringIO
from os import PathLike
from pathlib import Path
from typing import Any
from typing import TypeVar

from pydantic import BaseModel
from ruamel.yaml import YAML

from dapla_metadata.variable_definitions._generated.vardef_client.models.complete_response import (
    CompleteResponse,
)
from dapla_metadata.variable_definitions._utils.constants import HEADER
from dapla_metadata.variable_definitions._utils.files import _create_file_name
from dapla_metadata.variable_definitions._utils.files import _get_current_time
from dapla_metadata.variable_definitions._utils.files import (
    _model_to_yaml_with_comments,
)
from dapla_metadata.variable_definitions._utils.files import configure_yaml
from dapla_metadata.variable_definitions._utils.files import pre_process_data

logger = logging.getLogger(__name__)


T = TypeVar("T", bound=BaseModel)


def create_variable_yaml(
    model_instance: CompleteResponse,
    custom_directory: Path | None = None,
) -> Path:
    """Creates a yaml file for an existing variable definition."""
    file_name = _create_file_name(
        "variable_definition",
        _get_current_time(),
        model_instance.short_name,
        model_instance.id,
    )

    return _model_to_yaml_with_comments(
        model_instance,
        file_name,
        HEADER,
        custom_directory=custom_directory,
    )


def _read_variable_definition_file(file_path: Path) -> dict:
    yaml = YAML()
    configure_yaml(yaml)
    logger.debug("Full path to variable definition file %s", file_path)
    logger.info("Reading from '%s'", file_path.name)
    with file_path.open(encoding="utf-8") as f:
        return yaml.load(f)


def _strip_strings_recursively(data: Any) -> Any:
    """Recursively strip leading and trailing whitespace from string values in nested dicts/lists.

    This function traverses the provided data, which may be a dictionary, list, or other types,
    and applies the following logic:
        - If the data is a dictionary, it recursively strips string values in all key-value pairs.
        - If the data is a list, it recursively strips string values in all list elements.
        - If the data is a string, it strips leading and trailing whitespace.
        - Any other data types are returned unchanged.

    Args:
        data: The input data, which may include nested dictionaries, lists, or other types.

    Returns:
        Any: The processed data, with strings stripped of whitespace or unchanged if not a string.
    """
    if isinstance(data, dict):
        return {k: _strip_strings_recursively(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_strip_strings_recursively(item) for item in data]
    if isinstance(data, str):
        return data.strip()
    return data


def _read_file_to_model(
    file_path: PathLike[str] | None,
    model_class: type[T],
) -> T:
    """Read from a variable definition file into the given Pydantic model.

    Args:
        file_path (PathLike[str]): The path to the file to read in.
        model_class (type[T]): The model to instantiate. Must inherit from Pydantic's BaseModel.

    Raises:
        TypeError: If no file path could be deduced.
        FileNotFoundError: If we could not instantiate the model.

    Returns:
        T: BaseModel: The instantiated Pydantic model
    """
    try:
        file_path = Path(
            # type incongruence (i.e. None) is handled by catching the exception
            file_path,  # type: ignore [arg-type]
        )
    except TypeError as e:
        msg = "Could not deduce a path to the file. Please supply a path to the yaml file you wish to submit with the `file_path` parameter."
        raise FileNotFoundError(
            msg,
        ) from e
    raw_data = _read_variable_definition_file(file_path)
    cleaned_data = _strip_strings_recursively(raw_data)

    model = model_class.from_dict(  # type:ignore [attr-defined]
        cleaned_data
    )

    if model is None:
        msg = f"Could not read data from {file_path}"
        raise FileNotFoundError(msg)
    return model


def _convert_to_yaml_output(model: BaseModel) -> str:
    """Convert a Pydantic model to YAML format.

    Args:
        model: A Pydantic model instance

    Returns:
        YAML string representation of the model
    """
    stream = StringIO()
    with YAML(output=stream) as yaml:
        configure_yaml(yaml)
        data = model.model_dump(
            mode="json",
            serialize_as_any=True,
            warnings="error",
        )
        yaml.dump(pre_process_data(data))
    return stream.getvalue()
