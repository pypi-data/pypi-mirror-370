# vardef_client.VariableDefinitionsApi

All URIs are relative to *https://metadata.intern.test.ssb.no*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_public_variable_definition_by_id_0**](VariableDefinitionsApi.md#get_public_variable_definition_by_id_0) | **GET** /public/variable-definitions/{variable-definition-id} | Get one variable definition.
[**get_variable_definition_by_id**](VariableDefinitionsApi.md#get_variable_definition_by_id) | **GET** /variable-definitions/{variable-definition-id} | Get one variable definition.
[**list_public_variable_definitions_0**](VariableDefinitionsApi.md#list_public_variable_definitions_0) | **GET** /public/variable-definitions | List all variable definitions.
[**list_variable_definitions**](VariableDefinitionsApi.md#list_variable_definitions) | **GET** /variable-definitions | List all variable definitions.


# **get_public_variable_definition_by_id_0**
> get_public_variable_definition_by_id_0(variable_definition_id, accept_language, date_of_validity=date_of_validity)

Get one variable definition.

Get one variable definition. This is rendered in the given language, with the default being Norwegian Bokmål.

### Example


```python
import vardef_client
from vardef_client.models.supported_languages import SupportedLanguages
from vardef_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://metadata.intern.test.ssb.no
# See configuration.py for a list of all supported configuration parameters.
configuration = vardef_client.Configuration(
    host = "https://metadata.intern.test.ssb.no"
)


# Enter a context with an instance of the API client
with vardef_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = vardef_client.VariableDefinitionsApi(api_client)
    variable_definition_id = 'wypvb3wd' # str | Unique identifier for the variable definition.
    accept_language = vardef_client.SupportedLanguages() # SupportedLanguages | Render the variable definition in the given language.
    date_of_validity = '' # date | List only variable definitions which are valid on this date. (optional)

    try:
        # Get one variable definition.
        api_instance.get_public_variable_definition_by_id_0(variable_definition_id, accept_language, date_of_validity=date_of_validity)
    except Exception as e:
        print("Exception when calling VariableDefinitionsApi->get_public_variable_definition_by_id_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **variable_definition_id** | **str**| Unique identifier for the variable definition. | 
 **accept_language** | [**SupportedLanguages**](.md)| Render the variable definition in the given language. | 
 **date_of_validity** | **date**| List only variable definitions which are valid on this date. | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Ok |  -  |
**404** | No such variable definition found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_variable_definition_by_id**
> get_variable_definition_by_id(variable_definition_id, date_of_validity=date_of_validity)

Get one variable definition.

Get one variable definition.

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
    api_instance = vardef_client.VariableDefinitionsApi(api_client)
    variable_definition_id = 'wypvb3wd' # str | Unique identifier for the variable definition.
    date_of_validity = '' # date | List only variable definitions which are valid on this date. (optional)

    try:
        # Get one variable definition.
        api_instance.get_variable_definition_by_id(variable_definition_id, date_of_validity=date_of_validity)
    except Exception as e:
        print("Exception when calling VariableDefinitionsApi->get_variable_definition_by_id: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **variable_definition_id** | **str**| Unique identifier for the variable definition. | 
 **date_of_validity** | **date**| List only variable definitions which are valid on this date. | [optional] 

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

# **list_public_variable_definitions_0**
> list_public_variable_definitions_0(accept_language, date_of_validity=date_of_validity)

List all variable definitions.

List all variable definitions. These are rendered in the given language, with the default being Norwegian Bokmål.

### Example


```python
import vardef_client
from vardef_client.models.supported_languages import SupportedLanguages
from vardef_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://metadata.intern.test.ssb.no
# See configuration.py for a list of all supported configuration parameters.
configuration = vardef_client.Configuration(
    host = "https://metadata.intern.test.ssb.no"
)


# Enter a context with an instance of the API client
with vardef_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = vardef_client.VariableDefinitionsApi(api_client)
    accept_language = vardef_client.SupportedLanguages() # SupportedLanguages | Render the variable definition in the given language.
    date_of_validity = '' # str | List only variable definitions which are valid on this date. (optional)

    try:
        # List all variable definitions.
        api_instance.list_public_variable_definitions_0(accept_language, date_of_validity=date_of_validity)
    except Exception as e:
        print("Exception when calling VariableDefinitionsApi->list_public_variable_definitions_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **accept_language** | [**SupportedLanguages**](.md)| Render the variable definition in the given language. | 
 **date_of_validity** | **str**| List only variable definitions which are valid on this date. | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_variable_definitions**
> list_variable_definitions(date_of_validity=date_of_validity)

List all variable definitions.

List all variable definitions.

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
    api_instance = vardef_client.VariableDefinitionsApi(api_client)
    date_of_validity = '' # str | List only variable definitions which are valid on this date. (optional)

    try:
        # List all variable definitions.
        api_instance.list_variable_definitions(date_of_validity=date_of_validity)
    except Exception as e:
        print("Exception when calling VariableDefinitionsApi->list_variable_definitions: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **date_of_validity** | **str**| List only variable definitions which are valid on this date. | [optional] 

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
**200** | OK response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

