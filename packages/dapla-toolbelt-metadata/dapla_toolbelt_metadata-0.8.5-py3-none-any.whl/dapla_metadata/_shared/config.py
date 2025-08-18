"""Configuration management for dataset package."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from pprint import pformat

from dotenv import dotenv_values
from dotenv import load_dotenv

from dapla_metadata._shared.enums import DaplaEnvironment
from dapla_metadata._shared.enums import DaplaRegion
from dapla_metadata._shared.enums import DaplaService
from dapla_metadata.datasets.utility.constants import (
    DATADOC_STATISTICAL_SUBJECT_SOURCE_URL,
)

logger = logging.getLogger(__name__)

DOT_ENV_FILE_PATH = Path(__file__).parent.joinpath(".env")

JUPYTERHUB_USER = "JUPYTERHUB_USER"
DAPLA_REGION = "DAPLA_REGION"
DAPLA_ENVIRONMENT = "DAPLA_ENVIRONMENT"
DAPLA_SERVICE = "DAPLA_SERVICE"
DAPLA_GROUP_CONTEXT = "DAPLA_GROUP_CONTEXT"
OIDC_TOKEN = "OIDC_TOKEN"  # noqa: S105

env_loaded = False


def _load_dotenv_file() -> None:
    global env_loaded  # noqa: PLW0603
    if not env_loaded and DOT_ENV_FILE_PATH.exists():
        load_dotenv(DOT_ENV_FILE_PATH)
        env_loaded = True
        logger.info(
            "Loaded .env file with config keys: \n%s",
            pformat(list(dotenv_values(DOT_ENV_FILE_PATH).keys())),
        )


def get_config_item(item: str, *, raising: bool = False) -> str | None:
    """Get a config item. Makes sure all access is logged.

    Args:
        item: The name of the environment variable to obtain.
        raising: `True` if an exception should be raised when the item isn't present.

    Returns:
        The set value or `None`

    Raises:
        OSError: Only if `raising` is True and the item is not found.
    """
    _load_dotenv_file()
    value = os.environ.get(item)
    if raising and not value:
        msg = f"Environment variable {item} not defined."
        raise OSError(msg)
    logger.debug("Config accessed. %s", item)
    return value


def get_jupyterhub_user() -> str | None:
    """Get the JupyterHub user name."""
    return get_config_item(JUPYTERHUB_USER)


def get_statistical_subject_source_url() -> str | None:
    """Get the URL to the statistical subject source."""
    return (
        get_config_item("DATADOC_STATISTICAL_SUBJECT_SOURCE_URL")
        or DATADOC_STATISTICAL_SUBJECT_SOURCE_URL
    )


def get_dapla_region() -> DaplaRegion | None:
    """Get the Dapla region we're running on."""
    if region := get_config_item(DAPLA_REGION):
        return DaplaRegion(region)

    return None


def get_dapla_environment() -> DaplaEnvironment | None:
    """Get the Dapla environment we're running on."""
    if env := get_config_item(DAPLA_ENVIRONMENT):
        return DaplaEnvironment(env)

    return None


def get_dapla_service() -> DaplaService | None:
    """Get the Dapla service we're running on."""
    if service := get_config_item(DAPLA_SERVICE):
        return DaplaService(service)

    return None


def get_oidc_token(*, raising: bool = False) -> str | None:
    """Get the JWT token from the environment."""
    return get_config_item(OIDC_TOKEN, raising=raising)


def get_dapla_group_context(*, raising: bool = False) -> str | None:
    """Get the group which the user has chosen to represent."""
    return get_config_item(DAPLA_GROUP_CONTEXT, raising=raising)
