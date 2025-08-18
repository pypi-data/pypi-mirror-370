# vardef_client.PatchesApi

All URIs are relative to *https://metadata.intern.test.ssb.no*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_patch**](PatchesApi.md#create_patch) | **POST** /variable-definitions/{variable-definition-id}/patches | Create a new patch for a variable definition.
[**get_all_patches**](PatchesApi.md#get_all_patches) | **GET** /variable-definitions/{variable-definition-id}/patches | List all patches for the given variable definition.
[**get_one_patch**](PatchesApi.md#get_one_patch) | **GET** /variable-definitions/{variable-definition-id}/patches/{patch-id} | Get one concrete patch for the given variable definition.


# **create_patch**
> create_patch(variable_definition_id, active_group, patch, valid_from=valid_from)

Create a new patch for a variable definition.

Create a new patch for a variable definition.

### Example

* Bearer (JWT) Authentication (Keycloak token):

```python
import vardef_client
from vardef_client.models.patch import Patch
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
    api_instance = vardef_client.PatchesApi(api_client)
    variable_definition_id = 'wypvb3wd' # str | Unique identifier for the variable definition.
    active_group = 'dapla-felles-developers' # str | The group which the user currently represents.
    patch = vardef_client.Patch() # Patch | 
    valid_from = '1970-01-01' # date | Valid from date for the specific validity period to be patched. (optional)

    try:
        # Create a new patch for a variable definition.
        api_instance.create_patch(variable_definition_id, active_group, patch, valid_from=valid_from)
    except Exception as e:
        print("Exception when calling PatchesApi->create_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **variable_definition_id** | **str**| Unique identifier for the variable definition. | 
 **active_group** | **str**| The group which the user currently represents. | 
 **patch** | [**Patch**](Patch.md)|  | 
 **valid_from** | **date**| Valid from date for the specific validity period to be patched. | [optional] 

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
**400** | Bad request. |  -  |
**405** | Method only allowed for published variables. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_all_patches**
> get_all_patches(variable_definition_id)

List all patches for the given variable definition.

List all patches for the given variable definition. The full object is returned for comparison purposes.

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
    api_instance = vardef_client.PatchesApi(api_client)
    variable_definition_id = 'wypvb3wd' # str | Unique identifier for the variable definition.

    try:
        # List all patches for the given variable definition.
        api_instance.get_all_patches(variable_definition_id)
    except Exception as e:
        print("Exception when calling PatchesApi->get_all_patches: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **variable_definition_id** | **str**| Unique identifier for the variable definition. | 

### Return type

void (empty response body)

### Authorization

[Keycloak token](../README.md#Keycloak token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**404** | No such variable definition found |  -  |
**200** | Ok |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_one_patch**
> get_one_patch(variable_definition_id, patch_id)

Get one concrete patch for the given variable definition.

Get one concrete patch for the given variable definition. The full object is returned for comparison purposes.

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
    api_instance = vardef_client.PatchesApi(api_client)
    variable_definition_id = 'wypvb3wd' # str | Unique identifier for the variable definition.
    patch_id = 1 # int | ID of the patch to retrieve

    try:
        # Get one concrete patch for the given variable definition.
        api_instance.get_one_patch(variable_definition_id, patch_id)
    except Exception as e:
        print("Exception when calling PatchesApi->get_one_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **variable_definition_id** | **str**| Unique identifier for the variable definition. | 
 **patch_id** | **int**| ID of the patch to retrieve | 

### Return type

void (empty response body)

### Authorization

[Keycloak token](../README.md#Keycloak token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Ok |  -  |
**404** | No such variable definition found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

