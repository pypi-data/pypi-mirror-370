from __future__ import annotations

import contextlib
import logging
from typing import Protocol

import jwt

from dapla_metadata._shared import config
from dapla_metadata._shared.enums import DaplaRegion
from dapla_metadata._shared.enums import DaplaService

logger = logging.getLogger(__name__)


class UserInfo(Protocol):
    """Information about the current user.

    Implementations may be provided for different platforms or testing.
    """

    @property
    def short_email(self) -> str | None:
        """Get the short email address."""
        ...

    @property
    def current_group(self) -> str:
        """Get the group which the user is currently representing."""
        ...

    @property
    def current_team(self) -> str:
        """Get the team which the user is currently representing."""
        ...


class UnknownUserInfo:
    """Fallback when no implementation is found."""

    @property
    def short_email(self) -> str | None:
        """Unknown email address."""
        return None

    @property
    def current_group(self) -> str:
        """Get the group which the user is currently representing."""
        return ""

    @property
    def current_team(self) -> str:
        """Get the team which the user is currently representing."""
        return ""


class TestUserInfo:
    """Information about the current user for local development and testing."""

    PLACEHOLDER_EMAIL_ADDRESS = "default_user@ssb.no"
    PLACEHOLDER_GROUP = "default-team-developers"
    PLACEHOLDER_TEAM = "default-team"

    @property
    def short_email(self) -> str | None:
        """Get the short email address."""
        return TestUserInfo.PLACEHOLDER_EMAIL_ADDRESS

    @property
    def current_group(self) -> str | None:
        """Get the group which the user is currently representing."""
        return TestUserInfo.PLACEHOLDER_GROUP

    @property
    def current_team(self) -> str | None:
        """Get the team which the user is currently representing."""
        return TestUserInfo.PLACEHOLDER_TEAM


class DaplaLabUserInfo:
    """Information about the current user when running on Dapla Lab."""

    @property
    def short_email(self) -> str | None:
        """Get the short email address."""
        encoded_jwt = config.get_oidc_token()
        if encoded_jwt:
            # The JWT has been verified by the platform prior to injection, no need to verify.
            decoded_jwt = jwt.decode(encoded_jwt, options={"verify_signature": False})
            with contextlib.suppress(KeyError):
                # If email can't be found in the JWT, fall through and return None
                return decoded_jwt["email"]

        logger.warning(
            "Could not access JWT from environment. Could not get short email address.",
        )
        return None

    @property
    def current_group(self) -> str:
        """Get the group which the user is currently representing."""
        if group := config.get_dapla_group_context():
            return group
        msg = "DAPLA_GROUP_CONTEXT environment variable not found"
        raise OSError(msg)

    @property
    def current_team(self) -> str:
        """Get the team which the user is currently representing."""
        return parse_team_name(self.current_group)


class JupyterHubUserInfo:
    """Information about the current user when running on JupyterHub."""

    @property
    def short_email(self) -> str | None:
        """Get the short email address."""
        return config.get_jupyterhub_user()

    @property
    def current_group(self) -> str:
        """Get the group which the user is currently representing."""
        raise NotImplementedError

    @property
    def current_team(self) -> str:
        """Get the team which the user is currently representing."""
        raise NotImplementedError


def get_user_info_for_current_platform() -> UserInfo:
    """Return the correct implementation of UserInfo for the current platform."""
    if config.get_dapla_region() == DaplaRegion.DAPLA_LAB:
        return DaplaLabUserInfo()
    elif config.get_dapla_service() == DaplaService.JUPYTERLAB:  # noqa: RET505
        return JupyterHubUserInfo()
    else:
        logger.warning(
            "Was not possible to retrieve user information! Some fields may not be set.",
        )
        return UnknownUserInfo()


def parse_team_name(group: str) -> str:
    """Parses the group to get the current team.

    >>> parse_team_name("dapla-metadata-developers")
    'dapla-metadata'

    >>> parse_team_name("dapla-metadata-data-admins")
    'dapla-metadata'

    >>> parse_team_name("dapla-metadata")
    'dapla'

    >>> parse_team_name("dapla-metadata-not-real-name")
    'dapla-metadata-not-real'
    """
    parts = group.split("-")
    return "-".join(parts[:-2] if group.endswith("data-admins") else parts[:-1])
