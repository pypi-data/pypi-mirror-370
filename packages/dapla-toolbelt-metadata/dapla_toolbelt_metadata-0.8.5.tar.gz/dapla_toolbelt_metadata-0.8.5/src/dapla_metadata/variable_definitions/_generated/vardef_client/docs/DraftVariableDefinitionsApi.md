# vardef_client.DraftVariableDefinitionsApi

All URIs are relative to *https://metadata.intern.test.ssb.no*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_variable_definition**](DraftVariableDefinitionsApi.md#create_variable_definition) | **POST** /variable-definitions | Create a variable definition.
[**delete_variable_definition_by_id**](DraftVariableDefinitionsApi.md#delete_variable_definition_by_id) | **DELETE** /variable-definitions/{variable-definition-id} | Delete a variable definition.
[**update_variable_definition_by_id**](DraftVariableDefinitionsApi.md#update_variable_definition_by_id) | **PATCH** /variable-definitions/{variable-definition-id} | Update a variable definition.


# **create_variable_definition**
> create_variable_definition(active_group, draft)

Create a variable definition.

Create a variable definition. New variable definitions are automatically assigned status DRAFT and must include all required fields. Attempts to specify id or variable_status in a request will receive 400 BAD REQUEST responses.

### Example

* Bearer (JWT) Authentication (Keycloak token):

```python
import vardef_client
from vardef_client.models.draft import Draft
from vardef_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://metadata.intern.test.ssb.no
# See configuration.py for a list of all supported configuration parameters.
configuration = vardef_client.Configuration(
    host = "https://metadata.intern.test.ssb.no"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): Keycloak token
configuration = vardef_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with vardef_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = vardef_client.DraftVariableDefinitionsApi(api_client)
    active_group = 'dapla-felles-developers' # str | The group which the user currently represents.
    draft = vardef_client.Draft() # Draft | 

    try:
        # Create a variable definition.
        api_instance.create_variable_definition(active_group, draft)
    except Exception as e:
        print("Exception when calling DraftVariableDefinitionsApi->create_variable_definition: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **active_group** | **str**| The group which the user currently represents. | 
 **draft** | [**Draft**](Draft.md)|  | 

### Return type

void (empty response body)

### Authorization

[Keycloak token](../README.md#Keycloak token)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successfully created. |  -  |
**400** | Malformed data, missing data or attempt to specify disallowed fields. |  -  |
**409** | Short name is already in use by another variable definition. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_variable_definition_by_id**
> object delete_variable_definition_by_id(variable_definition_id, active_group)

Delete a variable definition.

Delete a variable definition.

### Example

* Bearer (JWT) Authentication (Keycloak token):

```python
import vardef_client
from vardef_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://metadata.intern.test.ssb.no
# See configuration.py for a list of all supported configuration parameters.
configuration = vardef_client.Configuration(
    host = "https://metadata.intern.test.ssb.no"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): Keycloak token
configuration = vardef_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with vardef_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = vardef_client.DraftVariableDefinitionsApi(api_client)
    variable_definition_id = 'wypvb3wd' # str | Unique identifier for the variable definition.
    active_group = 'dapla-felles-developers' # str | The group which the user currently represents.

    try:
        # Delete a variable definition.
        api_response = api_instance.delete_variable_definition_by_id(variable_definition_id, active_group)
        print("The response of DraftVariableDefinitionsApi->delete_variable_definition_by_id:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DraftVariableDefinitionsApi->delete_variable_definition_by_id: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **variable_definition_id** | **str**| Unique identifier for the variable definition. | 
 **active_group** | **str**| The group which the user currently represents. | 

### Return type

**object**

### Authorization

[Keycloak token](../README.md#Keycloak token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successfully deleted |  -  |
**404** | No such variable definition found |  -  |
**405** | Attempt to delete a variable definition with status unlike DRAFT. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_variable_definition_by_id**
> CompleteResponse update_variable_definition_by_id(variable_definition_id, active_group, update_draft)

Update a variable definition.

Update a variable definition. Only the fields which need updating should be supplied.

### Example

* Bearer (JWT) Authentication (Keycloak token):

```python
import vardef_client
from vardef_client.models.complete_response import CompleteResponse
from vardef_client.models.update_draft import UpdateDraft
from vardef_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://metadata.intern.test.ssb.no
# See configuration.py for a list of all supported configuration parameters.
configuration = vardef_client.Configuration(
    host = "https://metadata.intern.test.ssb.no"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): Keycloak token
configuration = vardef_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with vardef_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = vardef_client.DraftVariableDefinitionsApi(api_client)
    variable_definition_id = 'variable_definition_id_example' # str | 
    active_group = 'dapla-felles-developers' # str | The group which the user currently represents.
    update_draft = vardef_client.UpdateDraft() # UpdateDraft | 

    try:
        # Update a variable definition.
        api_response = api_instance.update_variable_definition_by_id(variable_definition_id, active_group, update_draft)
        print("The response of DraftVariableDefinitionsApi->update_variable_definition_by_id:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DraftVariableDefinitionsApi->update_variable_definition_by_id: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **variable_definition_id** | **str**|  | 
 **active_group** | **str**| The group which the user currently represents. | 
 **update_draft** | [**UpdateDraft**](UpdateDraft.md)|  | 

### Return type

[**CompleteResponse**](CompleteResponse.md)

### Authorization

[Keycloak token](../README.md#Keycloak token)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successfully updated |  -  |
**400** | Bad request. Examples of these are: - Reference to a Klass classification which doesn&#39;t exist. - Owner information missing. - Malformed email addresses. |  -  |
**404** | No such variable definition found |  -  |
**405** | Attempt to patch a variable definition with status unlike DRAFT. |  -  |
**409** | Short name is already in use by another variable definition. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

