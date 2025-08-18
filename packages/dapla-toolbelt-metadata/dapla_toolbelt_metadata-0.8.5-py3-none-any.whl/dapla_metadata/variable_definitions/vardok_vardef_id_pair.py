import logging
from pathlib import Path

from pydantic import ConfigDict
from pydantic import PrivateAttr

from dapla_metadata.variable_definitions._generated.vardef_client.models.vardok_vardef_id_pair_response import (
    VardokVardefIdPairResponse,
)
from dapla_metadata.variable_definitions._utils.variable_definition_files import (
    _convert_to_yaml_output,
)

logger = logging.getLogger(__name__)


class VardokVardefIdPair(VardokVardefIdPairResponse):
    """A Vardok id.

    - Provides access to the fields of a Vardok Vardef id pair.
    - Provides methods allowing for nicer output of the Vardok Vardef id pair.

    Args:
        VardokVardefIdPairResponse: The Pydantic model superclass, representing a Vardok Vardef id pair response.
    """

    _file_path: Path | None = PrivateAttr(None)
    model_config = ConfigDict(use_enum_values=True, str_strip_whitespace=True)

    @staticmethod
    def from_model(
        model: VardokVardefIdPairResponse,
    ) -> "VardokVardefIdPair":
        """Create a VardokVardefIdPair instance from a VardokVardefIdPairResponse."""
        return VardokVardefIdPair.model_construct(**model.model_dump())

    def __str__(self) -> str:
        """Format as indented YAML."""
        return _convert_to_yaml_output(self)

    def __repr__(self) -> str:
        """Format as indented YAML."""
        return _convert_to_yaml_output(self)
