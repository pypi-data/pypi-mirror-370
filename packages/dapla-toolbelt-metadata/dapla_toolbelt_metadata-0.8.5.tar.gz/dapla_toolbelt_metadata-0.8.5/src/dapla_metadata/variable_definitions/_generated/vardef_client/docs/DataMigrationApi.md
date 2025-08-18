# vardef_client.DataMigrationApi

All URIs are relative to *https://metadata.intern.test.ssb.no*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_variable_definition_from_var_dok**](DataMigrationApi.md#create_variable_definition_from_var_dok) | **POST** /vardok-migration/{vardok-id} | Create a variable definition from a VarDok variable definition.


# **create_variable_definition_from_var_dok**
> CompleteResponse create_variable_definition_from_var_dok(vardok_id, active_group)

Create a variable definition from a VarDok variable definition.

Create a variable definition from a VarDok variable definition.

### Example

* Bearer (JWT) Authentication (Keycloak token):

```python
import vardef_client
from vardef_client.models.complete_response import CompleteResponse
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
    api_instance = vardef_client.DataMigrationApi(api_client)
    vardok_id = '1607' # str | The ID of the definition in Vardok.
    active_group = 'dapla-felles-developers' # str | The group which the user currently represents.

    try:
        # Create a variable definition from a VarDok variable definition.
        api_response = api_instance.create_variable_definition_from_var_dok(vardok_id, active_group)
        print("The response of DataMigrationApi->create_variable_definition_from_var_dok:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataMigrationApi->create_variable_definition_from_var_dok: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **vardok_id** | **str**| The ID of the definition in Vardok. | 
 **active_group** | **str**| The group which the user currently represents. | 

### Return type

[**CompleteResponse**](CompleteResponse.md)

### Authorization

[Keycloak token](../README.md#Keycloak token)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successfully created. |  -  |
**400** | The definition in Vardok has missing or malformed metadata. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

