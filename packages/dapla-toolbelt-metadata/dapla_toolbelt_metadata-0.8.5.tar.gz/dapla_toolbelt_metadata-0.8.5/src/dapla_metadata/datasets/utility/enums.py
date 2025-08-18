"""Enumerations used in Datadoc."""

from __future__ import annotations

from enum import Enum


class SupportedLanguages(str, Enum):
    """The list of languages metadata may be recorded in.

    Reference: https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry
    """

    NORSK_BOKMÅL = "nb"  # noqa: PLC2401 the listed problems do not apply in this case
    NORSK_NYNORSK = "nn"
    ENGLISH = "en"
