import asyncio
import logging
import os
import time
from collections.abc import AsyncGenerator

from dapla_metadata.datasets.utility.utils import normalize_path
from dapla_metadata.standards.name_validator import NamingStandardReport
from dapla_metadata.standards.name_validator import ValidationResult
from dapla_metadata.standards.name_validator import validate_directory

logger = logging.getLogger(__name__)


async def check_naming_standard(
    file_path: str | os.PathLike[str],
) -> list[ValidationResult]:
    """Check whether a given path follows the SSB naming standard.

    This function checks whether the provided `file_path` and subdirectories thereof comply
    with the naming standard. Currently we only examine '.parquet' files. Other files are ignored.

    Args:
        file_path: The path to a bucket, directory, or specific file to validate.
                This can be in the following forms:
                  - A bucket URL in the form 'gs://ssb-dapla-felles-data-produkt-test'
                  - An absolute path to a mounted bucket in the form '/buckets/produkt'
                  - Any subdirectory or file thereof
                We also accept paths which don't yet exist so that you can test if a path will comply.

    Returns:
        list[ValidationResult]: A list of validation results,
        including success status, checked file path, messages, and any detected violations.

    Examples:
        >>> check_naming_standard("/data/example_file.parquet").success
        False

        >>> check_naming_standard("/buckets/produkt/datadoc/utdata/person_data_p2021_v2.parquet").success
        True
    """
    results = []

    # Begin validation.
    # For each file this returns a task which we can wait on to complete.
    # For each directory this returns another AsyncGenerator which must be unpacked below
    tasks = [t async for t in validate_directory(normalize_path(str(file_path)))]  # type:ignore [arg-type]

    # 5 minute timeout for safety
    start_time = time.time()
    while time.time() < start_time + (5 * 60):
        for item in tasks:
            if isinstance(item, AsyncGenerator):
                # Drill down into lower directories to get the validation tasks from them
                tasks.remove(item)
                new_tasks = [t async for t in item]
                logger.debug("New Tasks: %s %s", len(new_tasks), new_tasks)
                tasks.extend(
                    new_tasks,
                )
            elif isinstance(item, asyncio.Task):
                if item.done():
                    logger.info("Validated %s", item.get_name())
                    tasks.remove(item)
                    results.append(item.result())

        logger.debug("Tasks: %s %s", len(tasks), tasks)
        logger.debug("Results: %s", len(results))

        if len(tasks) == 0:
            logger.info("Completed validation")
            break

        # Allow time for other processing to be performed
        await asyncio.sleep(0.001)

    return results


def generate_validation_report(
    validation_results: list[ValidationResult],
) -> NamingStandardReport:
    """Generate and print a formatted naming standard validation report.

    This function takes a list of `ValidationResult` objects, creates a
    `NamingStandardReport` instance, and prints the generated report.

    Args:
        validation_results: A list of ValidationResult objects that
        contain the outcomes of the name standard checks.

    Returns:
        NamingStandardReport: An instance of `NamingStandardReport` containing
        the validation results.
    """
    report = NamingStandardReport(validation_results=validation_results)
    print(report.generate_report())  # noqa: T201
    return report
