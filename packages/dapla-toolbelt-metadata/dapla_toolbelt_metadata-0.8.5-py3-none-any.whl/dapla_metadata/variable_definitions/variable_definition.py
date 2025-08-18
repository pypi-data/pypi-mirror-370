import logging
from datetime import date
from os import PathLike
from pathlib import Path

from pydantic import ConfigDict
from pydantic import PrivateAttr

from dapla_metadata.variable_definitions._generated.vardef_client.api.draft_variable_definitions_api import (
    DraftVariableDefinitionsApi,
)
from dapla_metadata.variable_definitions._generated.vardef_client.api.patches_api import (
    PatchesApi,
)
from dapla_metadata.variable_definitions._generated.vardef_client.api.validity_periods_api import (
    ValidityPeriodsApi,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.complete_response import (
    CompleteResponse,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.patch import (
    Patch,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.update_draft import (
    UpdateDraft,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.validity_period import (
    ValidityPeriod,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.variable_status import (
    VariableStatus,
)
from dapla_metadata.variable_definitions._utils import config
from dapla_metadata.variable_definitions._utils._client import VardefClient
from dapla_metadata.variable_definitions._utils.variable_definition_files import (
    _convert_to_yaml_output,
)
from dapla_metadata.variable_definitions._utils.variable_definition_files import (
    _read_file_to_model,
)
from dapla_metadata.variable_definitions._utils.variable_definition_files import (
    create_variable_yaml,
)
from dapla_metadata.variable_definitions.exceptions import (
    publishing_blocked_error_handler,
)
from dapla_metadata.variable_definitions.exceptions import vardef_exception_handler
from dapla_metadata.variable_definitions.exceptions import vardef_file_error_handler

logger = logging.getLogger(__name__)


class VariableDefinition(CompleteResponse):
    """A Variable Definition.

    - Provides access to the fields of the specific Variable Definition.
    - Provides methods to access Patches and Validity Periods of this Variable Definition.
    - Provides methods allowing maintenance of this Variable Definition.

    Args:
        CompleteResponse: The Pydantic model superclass, representing a Variable Definition.
    """

    _file_path: Path | None = PrivateAttr(None)

    model_config = ConfigDict(use_enum_values=True, str_strip_whitespace=True)

    def get_file_path(self) -> Path | None:
        """Get the file path where the variable definition has been written to for editing."""
        return self._file_path

    def set_file_path(self, file_path: Path | None) -> None:
        """Set the file path where the variable definition has been written to for editing."""
        self._file_path = file_path

    @staticmethod
    def from_model(
        model: CompleteResponse,
    ) -> "VariableDefinition":
        """Create a VariableDefinition instance from a CompleteResponse."""
        return VariableDefinition.model_construct(**model.model_dump())

    @vardef_exception_handler
    def list_validity_periods(self) -> list["VariableDefinition"]:
        """List all Validity Periods for this Variable Definition."""
        return [
            VariableDefinition.from_model(validity_period)
            for validity_period in ValidityPeriodsApi(
                VardefClient.get_client(),
            ).list_validity_periods(
                variable_definition_id=self.id,
            )
        ]

    @vardef_exception_handler
    def list_patches(self) -> list["VariableDefinition"]:
        """List all Patches for this Variable Definition."""
        return [
            VariableDefinition.from_model(patch)
            for patch in PatchesApi(VardefClient.get_client()).list_patches(
                variable_definition_id=self.id,
            )
        ]

    @publishing_blocked_error_handler
    @vardef_exception_handler
    def update_draft(
        self,
        update_draft: UpdateDraft,
    ) -> "VariableDefinition":
        """Update this Variable Definition.

        - Variable definition must have status 'DRAFT'.
        - Supply only the fields to be changed. Other fields will retain their current values.

        Args:
            update_draft: The input with updated values.

        Returns:
            VariableDefinition: Updated Variable definition with all details.
        """
        updated = VariableDefinition.from_model(
            DraftVariableDefinitionsApi(
                VardefClient.get_client(),
            ).update_variable_definition_by_id(
                variable_definition_id=self.id,
                active_group=config.get_active_group(),
                update_draft=update_draft,
            ),
        )
        self.__dict__.update(updated)

        logger.info(
            "✅ Successfully updated variable definition '%s' with ID '%s'",
            updated.short_name,
            updated.id,
        )
        return updated

    @vardef_file_error_handler
    def update_draft_from_file(
        self,
        file_path: PathLike | None = None,
    ) -> "VariableDefinition":
        """Update this Variable Definition.

        Will automatically read the relevant file pertaining to this variable definition. Can
        be overridden by specifying the file_path parameter.

        - Variable definition must have status 'DRAFT'.
        - Supply only the fields to be changed. Other fields will retain their current values.

        Args:
            file_path: Optionally specify the path to read from.

        Returns:
            VariableDefinition: Updated Variable definition with all details.
        """
        return self.update_draft(
            _read_file_to_model(
                file_path or self.get_file_path(),
                UpdateDraft,
            ),
        )

    @vardef_exception_handler
    def delete_draft(
        self,
    ) -> str:
        """Delete this Variable definition.

        Variable definition must have status 'DRAFT'.

        Returns:
            str: A message if the operation was succsessful.

        """
        DraftVariableDefinitionsApi(
            VardefClient.get_client(),
        ).delete_variable_definition_by_id(
            variable_definition_id=self.id,
            active_group=config.get_active_group(),
        )
        return f"✅ Variable {self.id} safely deleted"

    @vardef_exception_handler
    def get_patch(self, patch_id: int) -> "VariableDefinition":
        """Get a single Patch by ID.

        Args:
            patch_id (int): The ID of the patch.

        Returns:
            VariableDefinition: The desired patch.
        """
        return VariableDefinition.from_model(
            PatchesApi(VardefClient.get_client()).get_patch(
                variable_definition_id=self.id,
                patch_id=patch_id,
            ),
        )

    @vardef_exception_handler
    def create_patch(
        self,
        patch: Patch,
        valid_from: date | None = None,
    ) -> "VariableDefinition":
        """Create a new Patch for this Variable Definition.

        Patches are to be used for minor changes which don't require a new Validity Period.
        Examples of reasons for creating a new Patch:
        - Correcting a typo
        - Adding a translation
        - Adding a subject field

        Supply only the fields to be changed. Other fields will retain their current values.

        Args:
            patch: The input for a new patch.
            valid_from: Optional date for selecting a Validity Period to create patch in. The date must
                        exactly match the Validity Period `valid_from`. If value is None the patch is
                        created in the last validity period.

        Returns:
            VariableDefinition: Variable Definition with all details.

        """
        new_patch = VariableDefinition.from_model(
            PatchesApi(
                VardefClient.get_client(),
            ).create_patch(
                variable_definition_id=self.id,
                active_group=config.get_active_group(),
                patch=patch,
                valid_from=valid_from,
            ),
        )
        self.__dict__.update(new_patch)

        logger.info(
            "✅ Successfully created patch with patch ID '%s' for variable definition '%s' with ID '%s'",
            new_patch.patch_id,
            new_patch.short_name,
            new_patch.id,
        )
        return new_patch

    @vardef_file_error_handler
    def create_patch_from_file(
        self,
        file_path: PathLike | None = None,
        valid_from: date | None = None,
    ) -> "VariableDefinition":
        """Create a new Patch for this Variable Definition from a file.

        Will automatically read the relevant file pertaining to this variable definition. Can
        be overridden by specifying the file_path parameter.

        Patches are to be used for minor changes which don't require a new Validity Period.
        Examples of reasons for creating a new Patch:
          - Correcting a typo
          - Adding a translation
          - Adding a subject field

        Supply only the fields to be changed. Other fields will retain their current values.

        Args:
            file_path: Optionally specify the path to read from.
            valid_from: Optional date for selecting a Validity Period to create patch in. The date must
                        exactly match the Validity Period `valid_from`. If value is None the patch is
                        created in the last validity period.

        Returns:
            VariableDefinition: Variable Definition with all details.
        """
        return self.create_patch(
            patch=_read_file_to_model(
                file_path or self.get_file_path(),
                Patch,
            ),
            valid_from=valid_from,
        )

    @vardef_exception_handler
    def create_validity_period(
        self,
        validity_period: ValidityPeriod,
    ) -> "VariableDefinition":
        """Create a new Validity Period for this Variable Definition.

        In order to create a new Validity Period input must contain updated
        'definition' text for all present languages and a new valid from.

        A new Validity Period should be created only when the fundamental definition
        of the variable has changed. This way the previous definition can be preserved
        for use in historical data.

        Args:
            validity_period: The input for new Validity Period

        Returns:
            VariableDefinition: Variable Definition with all details.
        """
        new_validity_period = VariableDefinition.from_model(
            ValidityPeriodsApi(
                VardefClient.get_client(),
            ).create_validity_period(
                variable_definition_id=self.id,
                active_group=config.get_active_group(),
                validity_period=validity_period,
            ),
        )
        self.__dict__.update(new_validity_period)

        logger.info(
            "✅ Successfully created validity period that is valid from '%s' for variable definition '%s' with ID '%s'",
            new_validity_period.valid_from,
            new_validity_period.short_name,
            new_validity_period.id,
        )
        return new_validity_period

    @vardef_file_error_handler
    def create_validity_period_from_file(
        self,
        file_path: PathLike | None = None,
    ) -> "VariableDefinition":
        """Create a new ValidityPeriod for this Variable Definition from a file.

        In order to create a new Validity Period the input file must contain updated
        'definition' text for all present languages and a new valid from.

        Args:
            file_path: Optionally specify the path to read from.

        Returns:
            VariableDefinition: Variable Definition with all details.
        """
        return self.create_validity_period(
            validity_period=_read_file_to_model(
                file_path or self.get_file_path(),
                ValidityPeriod,
            ),
        )

    @publishing_blocked_error_handler
    def publish_internal(self) -> "VariableDefinition":
        """Publish this variable definition internally."""
        if self.variable_status != VariableStatus.DRAFT.name:
            msg = "That won't work here. Only variable definitions with status DRAFT may be published internally."
            raise ValueError(
                msg,
            )
        update = self.update_draft(
            UpdateDraft(variable_status=VariableStatus.PUBLISHED_INTERNAL),
        )
        logger.info(
            "✅ Variable definition '%s' with ID '%s' successfully published, new status: %s",
            update.short_name,
            update.id,
            update.variable_status,
        )
        return update

    @publishing_blocked_error_handler
    def publish_external(self) -> "VariableDefinition":
        """Publish this variable definition externally."""
        if self.variable_status == VariableStatus.PUBLISHED_EXTERNAL.name:
            msg = "That won't work here. The variable definition is already published."
            raise ValueError(
                msg,
            )
        if self.variable_status is VariableStatus.DRAFT:
            update = self.update_draft(
                UpdateDraft(variable_status=VariableStatus.PUBLISHED_EXTERNAL),
            )
        else:
            update = self.create_patch(
                Patch(variable_status=VariableStatus.PUBLISHED_EXTERNAL),
            )
        logger.info(
            "✅ Variable definition '%s' with ID '%s' successfully published, new status: %s",
            update.short_name,
            update.id,
            update.variable_status,
        )
        return update

    def to_file(self) -> "VariableDefinition":
        """Write this variable definition to file."""
        file_path = create_variable_yaml(
            model_instance=self,
        )
        self.set_file_path(file_path)
        logger.info(
            f"✅ Created editable variable definition file at {file_path}",  # noqa: G004
        )
        return self

    def to_dict(self) -> dict:
        """Return as dictionary."""
        return super().to_dict()

    def __str__(self) -> str:
        """Format as indented YAML."""
        return _convert_to_yaml_output(self)

    def __repr__(self) -> str:
        """Format as indented YAML."""
        return _convert_to_yaml_output(self)
