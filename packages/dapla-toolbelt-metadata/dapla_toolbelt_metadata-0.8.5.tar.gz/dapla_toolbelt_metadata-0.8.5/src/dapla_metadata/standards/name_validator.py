import asyncio
import logging
import os
import re
from collections.abc import AsyncGenerator
from pathlib import Path

from dapla_metadata.datasets.dapla_dataset_path_info import DaplaDatasetPathInfo
from dapla_metadata.datasets.dataset_parser import SUPPORTED_DATASET_FILE_SUFFIXES
from dapla_metadata.standards.utils.constants import FILE_DOES_NOT_EXIST
from dapla_metadata.standards.utils.constants import FILE_IGNORED
from dapla_metadata.standards.utils.constants import IGNORED_FOLDERS
from dapla_metadata.standards.utils.constants import INVALID_SYMBOLS
from dapla_metadata.standards.utils.constants import MISSING_DATA_STATE
from dapla_metadata.standards.utils.constants import MISSING_DATASET_SHORT_NAME
from dapla_metadata.standards.utils.constants import MISSING_PERIOD
from dapla_metadata.standards.utils.constants import MISSING_SHORT_NAME
from dapla_metadata.standards.utils.constants import MISSING_VERSION
from dapla_metadata.standards.utils.constants import NAME_STANDARD_SUCCESS
from dapla_metadata.standards.utils.constants import NAME_STANDARD_VIOLATION
from dapla_metadata.standards.utils.constants import PATH_IGNORED
from dapla_metadata.standards.utils.constants import SSB_NAMING_STANDARD_REPORT
from dapla_metadata.standards.utils.constants import SSB_NAMING_STANDARD_REPORT_FILES
from dapla_metadata.standards.utils.constants import (
    SSB_NAMING_STANDARD_REPORT_RESULT_AVERAGE,
)
from dapla_metadata.standards.utils.constants import (
    SSB_NAMING_STANDARD_REPORT_RESULT_BEST,
)
from dapla_metadata.standards.utils.constants import (
    SSB_NAMING_STANDARD_REPORT_RESULT_GOOD,
)
from dapla_metadata.standards.utils.constants import (
    SSB_NAMING_STANDARD_REPORT_RESULT_LOW,
)
from dapla_metadata.standards.utils.constants import (
    SSB_NAMING_STANDARD_REPORT_RESULT_NO_SCORE,
)
from dapla_metadata.standards.utils.constants import SSB_NAMING_STANDARD_REPORT_SUCCESS
from dapla_metadata.standards.utils.constants import (
    SSB_NAMING_STANDARD_REPORT_SUCCESS_RATE,
)
from dapla_metadata.standards.utils.constants import (
    SSB_NAMING_STANDARD_REPORT_VIOLATIONS,
)

logger = logging.getLogger(__name__)


class ValidationResult:
    """Result object for name standard validation."""

    def __init__(
        self,
        success: bool,
        file_path: str,
    ) -> None:
        """Initialize the validatation result."""
        self.success = success
        self.file_path = file_path
        self.messages: list[str] = []
        self.violations: list[str] = []

    def add_message(self, message: str) -> None:
        """Add message to list."""
        if message not in self.messages:
            self.messages.append(message)

    def add_violation(self, violation: str) -> None:
        """Add violation to list."""
        if violation not in self.violations:
            self.violations.append(violation)
        if self.success:
            self.success = False

    def __repr__(self) -> str:
        """Representation for debugging."""
        return f"ValidationResult(success={self.success}, file_path={self.file_path}, messages={self.messages}, violations={self.violations})"

    def to_dict(self) -> dict:
        """Return result as a dictionary."""
        return {
            "success": self.success,
            "file_path": self.file_path,
            "messages": self.messages,
            "violations": self.violations,
        }


class NamingStandardReport:
    """Report object for name standard validation."""

    def __init__(self, validation_results: list[ValidationResult]) -> None:
        """Initialize the naming standard report."""
        self.validation_results = validation_results
        self.num_files_validated = len(validation_results)
        self.num_success = len(
            [result for result in validation_results if result.success is True],
        )
        self.num_failures = len(
            [result for result in validation_results if result.success is False],
        )

    def generate_report(self) -> str:
        """Format the report as a string."""
        return (
            f"{SSB_NAMING_STANDARD_REPORT}\n"
            f"=============================\n"
            f"{self.evaluate_result()}"
            f"{SSB_NAMING_STANDARD_REPORT_SUCCESS_RATE}: {self.success_rate():.2f}%\n"
            f"{SSB_NAMING_STANDARD_REPORT_FILES}: {self.num_files_validated}\n"
            f"{SSB_NAMING_STANDARD_REPORT_SUCCESS}: {self.num_success}\n"
            f"{SSB_NAMING_STANDARD_REPORT_VIOLATIONS}s: {self.num_failures}\n"
        )

    def success_rate(self) -> int | float | None:
        """Calculate the success rate as a percentage.

        Returns:
            int | float | None: The success rate as a percentage, or None if
            no files were validated.
        """
        if self.num_files_validated == 0:
            return None
        return self.num_success / self.num_files_validated * 100

    def evaluate_result(self) -> str:
        """Returns an appropriate message based on the success rate."""
        rate = self.success_rate()
        if rate is not None:
            if 95 <= rate <= 100:
                return SSB_NAMING_STANDARD_REPORT_RESULT_BEST
            if 70 < rate < 95:
                return SSB_NAMING_STANDARD_REPORT_RESULT_GOOD
            if 40 <= rate <= 70:
                return SSB_NAMING_STANDARD_REPORT_RESULT_AVERAGE
            if rate < 40:
                return SSB_NAMING_STANDARD_REPORT_RESULT_LOW
        return SSB_NAMING_STANDARD_REPORT_RESULT_NO_SCORE


def _has_invalid_symbols(path: os.PathLike[str]) -> bool:
    """Return True if string contains illegal symbols.

    Examples:
        >>> _has_invalid_symbols("åregang-øre")
        True

        >>> _has_invalid_symbols("Azor89")
        False

        >>> _has_invalid_symbols("ssbÆ-dapla-example-data-produkt-prod/ledstill/oppdrag/skjema_p2018_p2020_v1")
        True

        >>> _has_invalid_symbols("ssb-dapla-example-data-produkt-prod/ledstill/oppdrag/skjema_p2018_p2020_v1")
        False

        >>> _has_invalid_symbols("ssb-dapla-example-data-produkt-prod/ledstill/inndata/skjema_p2018_p202_v1/aar=2018/data.parquet")
        False
    """
    # TODO @mmwinther: The = symbol is allowed to avoid failures on subdirectories of partioned parquet datasets.
    # DPMETA-824
    return bool(re.search(r"[^a-zA-Z0-9\./:_\-=]", str(path).strip()))


def _check_violations(
    file: Path,
) -> list[str]:
    """Check for missing attributes and invalid symbols."""
    path_info = DaplaDatasetPathInfo(file)
    checks = {
        MISSING_SHORT_NAME: path_info.statistic_short_name,
        MISSING_DATA_STATE: path_info.dataset_state,
        MISSING_PERIOD: path_info.contains_data_from,
        MISSING_DATASET_SHORT_NAME: path_info.dataset_short_name,
        MISSING_VERSION: path_info.dataset_version,
        INVALID_SYMBOLS: not _has_invalid_symbols(file),
    }

    return [message for message, value in checks.items() if not value]


async def _validate_file(
    file: Path,
    check_file_exists: bool = False,
) -> ValidationResult:
    """Check for naming standard violations.

    Returns:
        A ValidationResult object containing messages and violations
    """
    logger.info("Validating file: %s", file)
    if file.suffix not in SUPPORTED_DATASET_FILE_SUFFIXES:
        logger.info("Skipping validation on non-dataset file: %s", file)
        return await _ignored_file_type_result(file)

    result = ValidationResult(success=True, file_path=str(file))

    if check_file_exists and not file.exists():
        result.add_message(
            FILE_DOES_NOT_EXIST,
        )

    result.violations = await asyncio.get_running_loop().run_in_executor(
        None,
        lambda: _check_violations(file),
    )

    if result.violations:
        result.success = False
        result.add_message(NAME_STANDARD_VIOLATION)
    else:
        result.success = True
        result.add_message(
            NAME_STANDARD_SUCCESS,
        )
    return result


async def _ignored_folder_result(file: Path) -> ValidationResult:
    r = ValidationResult(success=True, file_path=str(file))
    r.add_message(PATH_IGNORED)
    return r


async def _ignored_file_type_result(file: Path) -> ValidationResult:
    r = ValidationResult(success=True, file_path=str(file))
    r.add_message(FILE_IGNORED)
    return r


async def validate_directory(
    path: Path,
) -> AsyncGenerator[AsyncGenerator | asyncio.Task]:
    """Validate a file or recursively validate all files in a directory."""
    if set(path.parts).intersection(IGNORED_FOLDERS):
        logger.info("File path ignored: %s", path)
        yield asyncio.create_task(_ignored_folder_result(path))
    elif path.suffix:
        yield asyncio.create_task(_validate_file(path, check_file_exists=True))
    else:
        for obj in await asyncio.get_running_loop().run_in_executor(
            None,
            lambda: path.glob("*"),
        ):
            if obj.suffix:
                yield asyncio.create_task(_validate_file(obj), name=obj.name)
            else:
                logger.debug("Recursing into: %s", obj)
                yield validate_directory(obj)
