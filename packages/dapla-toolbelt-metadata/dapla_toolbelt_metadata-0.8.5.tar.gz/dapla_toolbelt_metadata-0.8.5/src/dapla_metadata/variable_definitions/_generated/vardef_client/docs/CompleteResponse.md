# CompleteResponse

Complete response For internal users who need all details while maintaining variable definitions.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Unique identifier for the variable definition. | [optional]
**patch_id** | **int** | Integer identifying a patch of a variable definition. |
**name** | [**LanguageStringType**](LanguageStringType.md) | Name of the variable. Must be unique for a given Unit Type and Owner combination. |
**short_name** | **str** | Recommended short name. Must be unique within an organization. |
**definition** | [**LanguageStringType**](LanguageStringType.md) | Definition of the variable. |
**classification_reference** | **str** | ID of a classification or code list from Klass. The given classification defines all possible values for the defined variable. | [optional]
**unit_types** | **List[str]** | A list of one or more unit types, e.g. person, vehicle, household. Must be defined as codes from https://www.ssb.no/klass/klassifikasjoner/702. |
**subject_fields** | **List[str]** | A list of subject fields that the variable is used in. Must be defined as codes from https://www.ssb.no/klass/klassifikasjoner/618. |
**contains_special_categories_of_personal_data** | **bool** | True if variable instances contain particularly sensitive information. Applies even if the information or identifiers are pseudonymized. Information within the following categories are regarded as particularly sensitive: Ethnicity, Political alignment, Religion, Philosophical beliefs, Union membership, Genetics, Biometrics, Health, Sexual relations, Sexual orientation |
**variable_status** | [**VariableStatus**](VariableStatus.md) | Status of the life cycle of the variable | [optional]
**measurement_type** | **str** | Type of measurement for the variable, e.g. length, volume, currency. Must be defined as codes from https://www.ssb.no/klass/klassifikasjoner/303 | [optional]
**valid_from** | **date** | The variable definition is valid from this date inclusive |
**valid_until** | **date** | The variable definition is valid until this date inclusive | [optional]
**external_reference_uri** | **str** | A link (URI) to an external definition/documentation | [optional]
**comment** | [**LanguageStringType**](LanguageStringType.md) | Optional comment to explain the definition or communicate potential changes. | [optional]
**related_variable_definition_uris** | **List[str]** | Link(s) to related definitions of variables - a list of one or more definitions. For example for a variable after-tax income it could be relevant to link to definitions of income from work, property income etc. | [optional]
**owner** | [**Owner**](Owner.md) | Owner of the definition, i.e. responsible Dapla team (statistics team) and information about access management groups. |
**contact** | [**Contact**](Contact.md) | Contact details | [optional]
**created_at** | **datetime** | The timestamp at which this variable definition was first created. |
**created_by** | **str** | The user who created this variable definition. | [optional]
**last_updated_at** | **datetime** | The timestamp at which this variable definition was last modified. |
**last_updated_by** | **str** | The user who last modified this variable definition. | [optional]

## Example

```python
from vardef_client.models.complete_response import CompleteResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CompleteResponse from a JSON string
complete_response_instance = CompleteResponse.from_json(json)
# print the JSON string representation of the object
print(CompleteResponse.to_json())

# convert the object into a dict
complete_response_dict = complete_response_instance.to_dict()
# create an instance of CompleteResponse from a dict
complete_response_from_dict = CompleteResponse.from_dict(complete_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


