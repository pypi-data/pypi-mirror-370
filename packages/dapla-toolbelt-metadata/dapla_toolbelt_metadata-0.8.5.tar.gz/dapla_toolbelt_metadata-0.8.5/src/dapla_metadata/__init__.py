"""Tools and clients for working with the Dapla Metadata system."""

import warnings

warnings.filterwarnings(
    "ignore",
    message="As the c extension couldn't be imported, `google-crc32c` is using a pure python implementation that is significantly slower.",
)

import datadoc_model.all_optional.model as datadoc_model

from . import dapla
from . import datasets
from . import standards
from . import variable_definitions
