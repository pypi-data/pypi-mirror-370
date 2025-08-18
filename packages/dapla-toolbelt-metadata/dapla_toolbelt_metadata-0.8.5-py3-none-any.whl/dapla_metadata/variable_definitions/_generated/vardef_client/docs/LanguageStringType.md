# LanguageStringType


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**nb** | **str** |  | [optional] 
**nn** | **str** |  | [optional] 
**en** | **str** |  | [optional] 

## Example

```python
from vardef_client.models.language_string_type import LanguageStringType

# TODO update the JSON string below
json = "{}"
# create an instance of LanguageStringType from a JSON string
language_string_type_instance = LanguageStringType.from_json(json)
# print the JSON string representation of the object
print(LanguageStringType.to_json())

# convert the object into a dict
language_string_type_dict = language_string_type_instance.to_dict()
# create an instance of LanguageStringType from a dict
language_string_type_from_dict = LanguageStringType.from_dict(language_string_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


