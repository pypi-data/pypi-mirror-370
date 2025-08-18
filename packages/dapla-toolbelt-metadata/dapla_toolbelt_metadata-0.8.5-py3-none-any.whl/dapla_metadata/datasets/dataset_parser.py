"""Abstractions for dataset file formats.

Handles reading in the data and transforming data types to generic metadata types.
"""

from __future__ import annotations

import pathlib  # noqa: TC003 import is needed for docs build
import re
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

import pandas as pd
from datadoc_model.all_optional.model import DataType
from datadoc_model.all_optional.model import LanguageStringType
from datadoc_model.all_optional.model import LanguageStringTypeItem
from datadoc_model.all_optional.model import Variable
from pyarrow import parquet as pq

from dapla_metadata.datasets.utility.enums import SupportedLanguages

if TYPE_CHECKING:
    import pyarrow as pa
    from cloudpathlib import CloudPath

KNOWN_INTEGER_TYPES = (
    "int",
    "int_",
    "int8",
    "int16",
    "int32",
    "int64",
    "integer",
    "long",
    "uint",
    "uint8",
    "uint16",
    "uint32",
    "uint64",
)

KNOWN_FLOAT_TYPES = (
    "double",
    "float",
    "float_",
    "float16",
    "float32",
    "float64",
    "decimal",
    "number",
    "numeric",
    "num",
)

KNOWN_STRING_TYPES = (
    "string",
    "string[pyarrow]",
    "large_string",
    "str",
    "char",
    "varchar",
    "varchar2",
    "text",
    "txt",
    "bytes",
)

KNOWN_DATETIME_TYPES = (
    "timestamp",
    "timestamp[s]",
    "timestamp[ms]",
    "timestamp[us]",
    "timestamp[ns]",
    "datetime",
    "datetime64",
    "datetime64[s]",
    "datetime64[ms]",
    "datetime64[us]",
    "datetime64[ns]",
    "date",
    "date32[day]",
    "time",
)

KNOWN_BOOLEAN_TYPES = ("bool", "bool_", "boolean")


TYPE_CORRESPONDENCE: list[tuple[tuple[str, ...], DataType]] = [
    (KNOWN_INTEGER_TYPES, DataType.INTEGER),
    (KNOWN_FLOAT_TYPES, DataType.FLOAT),
    (KNOWN_STRING_TYPES, DataType.STRING),
    (KNOWN_DATETIME_TYPES, DataType.DATETIME),
    (KNOWN_BOOLEAN_TYPES, DataType.BOOLEAN),
]
TYPE_MAP: dict[str, DataType] = {}
for concrete_type, abstract_type in TYPE_CORRESPONDENCE:
    TYPE_MAP.update(dict.fromkeys(concrete_type, abstract_type))


class DatasetParser(ABC):
    """Abstract Base Class for all Dataset parsers.

    Implements:
    - A static factory method to get the correct implementation for each file extension.
    - A static method for data type conversion.

    Requires implementation by subclasses:
    - A method to extract variables (columns) from the dataset, so they may be documented.
    """

    def __init__(self, dataset: pathlib.Path | CloudPath) -> None:
        """Initialize for a given dataset."""
        self.dataset = dataset

    @staticmethod
    def for_file(dataset: pathlib.Path | CloudPath) -> DatasetParser:
        """Return the correct subclass based on the given dataset file."""
        file_type = "Unknown"
        try:
            file_type = dataset.suffix
            # Gzipped parquet files can be read with DatasetParserParquet
            match = re.search(PARQUET_GZIP_FILE_SUFFIX, str(dataset).lower())
            file_type = PARQUET_GZIP_FILE_SUFFIX if match else file_type
            # Extract the appropriate reader class from the SUPPORTED_FILE_TYPES dict
            reader = SUPPORTED_DATASET_FILE_SUFFIXES[file_type](dataset)
        except IndexError as e:
            # Thrown when just one element is returned from split, meaning there is no file extension supplied
            msg = f"Could not recognise file type for provided {dataset = }. Supported file types are: {', '.join(SUPPORTED_DATASET_FILE_SUFFIXES.keys())}"
            raise FileNotFoundError(
                msg,
            ) from e
        except KeyError as e:
            # In this case the file type is not supported, so we throw a helpful exception
            msg = f"{file_type = } is not supported. Please open one of the following supported files types: {', '.join(SUPPORTED_DATASET_FILE_SUFFIXES.keys())} or contact the maintainers to request support."
            raise NotImplementedError(
                msg,
            ) from e
        else:
            return reader

    @staticmethod
    def transform_data_type(data_type: str) -> DataType | None:
        """Transform a concrete data type to an abstract data type.

        In statistical metadata, one is not interested in how the data is
        technically stored, but in the meaning of the data type. Because of
        this, we transform known data types to their abstract metadata
        representations.

        If we encounter a data type we don't know, we just ignore it and let
        the user handle it in the GUI.

        Arguments:
            data_type: The concrete data type to map.

        Returns:
            The abstract data type or None
        """
        return TYPE_MAP.get(data_type.lower(), None)

    @abstractmethod
    def get_fields(self) -> list[Variable]:
        """Abstract method, must be implemented by subclasses."""


class DatasetParserParquet(DatasetParser):
    """Concrete implementation for parsing parquet files."""

    def __init__(self, dataset: pathlib.Path | CloudPath) -> None:
        """Call the super init method for initialization.

        Args:
            dataset: Path to the dataset to parse.
        """
        super().__init__(dataset)

    def get_fields(self) -> list[Variable]:
        """Extract the fields from this dataset."""
        with self.dataset.open(mode="rb") as f:
            schema: pa.Schema = pq.read_schema(f)  # type: ignore [arg-type, assignment]
        return [
            Variable(
                short_name=data_field.name.strip(),
                data_type=self.transform_data_type(str(data_field.type)),  # type: ignore [attr-defined]
            )
            for data_field in schema
            if data_field.name
            != "__index_level_0__"  # Index columns should not be documented
        ]


class DatasetParserSas7Bdat(DatasetParser):
    """Concrete implementation for parsing SAS7BDAT files."""

    def __init__(self, dataset: pathlib.Path | CloudPath) -> None:
        """Call the super init method for initialization.

        Args:
            dataset: Path to the dataset to parse.
        """
        super().__init__(dataset)

    def get_fields(self) -> list[Variable]:
        """Extract the fields from this dataset."""
        fields = []
        with self.dataset.open(mode="rb") as f:
            # Use an iterator to avoid reading in the entire dataset
            sas_reader = pd.read_sas(f, format="sas7bdat", iterator=True)

            # Get the first row from the iterator
            try:
                row = next(sas_reader)
            except StopIteration as e:
                msg = f"Could not read data from {self.dataset}"
                raise RuntimeError(msg) from e

        # Get all the values from the row and loop through them
        for i, v in enumerate(row.to_numpy().tolist()[0]):
            fields.append(
                Variable(
                    short_name=sas_reader.columns[i].name,  # type: ignore [attr-defined]
                    # Assume labels are defined in the default language (NORSK_BOKMÅL)
                    # If this is not correct, the user may fix it via the UI
                    name=LanguageStringType(
                        [
                            LanguageStringTypeItem(
                                languageCode=SupportedLanguages.NORSK_BOKMÅL.value,
                                languageText=sas_reader.columns[  # type: ignore [attr-defined]
                                    i
                                ].label,
                            ),
                        ],
                    ),
                    # Access the python type for the value and transform it to a DataDoc Data type
                    data_type=self.transform_data_type(type(v).__name__.lower()),  # type: ignore  # noqa: PGH003
                ),
            )

        return fields


PARQUET_FILE_SUFFIX = ".parquet"
PARQUET_GZIP_FILE_SUFFIX = ".parquet.gzip"
SAS7BDAT_FILE_SUFFIX = ".sas7bdat"

SUPPORTED_DATASET_FILE_SUFFIXES: dict[
    str,
    type[DatasetParser],
] = {
    PARQUET_FILE_SUFFIX: DatasetParserParquet,
    PARQUET_GZIP_FILE_SUFFIX: DatasetParserParquet,
    SAS7BDAT_FILE_SUFFIX: DatasetParserSas7Bdat,
}
