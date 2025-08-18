# vardef_client.PublicApi

All URIs are relative to *https://metadata.intern.test.ssb.no*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_public_variable_definition_by_id**](PublicApi.md#get_public_variable_definition_by_id) | **GET** /public/variable-definitions/{variable-definition-id} | Get one variable definition.
[**list_public_validity_periods**](PublicApi.md#list_public_validity_periods) | **GET** /public/variable-definitions/{variable-definition-id}/validity-periods | List all validity periods.
[**list_public_variable_definitions**](PublicApi.md#list_public_variable_definitions) | **GET** /public/variable-definitions | List all variable definitions.


# **get_public_variable_definition_by_id**
> get_public_variable_definition_by_id(variable_definition_id, accept_language, date_of_validity=date_of_validity)

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
    api_instance = vardef_client.PublicApi(api_client)
    variable_definition_id = 'wypvb3wd' # str | Unique identifier for the variable definition.
    accept_language = vardef_client.SupportedLanguages() # SupportedLanguages | Render the variable definition in the given language.
    date_of_validity = '' # date | List only variable definitions which are valid on this date. (optional)

    try:
        # Get one variable definition.
        api_instance.get_public_variable_definition_by_id(variable_definition_id, accept_language, date_of_validity=date_of_validity)
    except Exception as e:
        print("Exception when calling PublicApi->get_public_variable_definition_by_id: %s\n" % e)
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

# **list_public_validity_periods**
> list_public_validity_periods(variable_definition_id, accept_language)

List all validity periods.

List all validity periods. These are rendered in the given language, with the default being Norwegian Bokmål.

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
    api_instance = vardef_client.PublicApi(api_client)
    variable_definition_id = 'wypvb3wd' # str | Unique identifier for the variable definition.
    accept_language = vardef_client.SupportedLanguages() # SupportedLanguages | Render the variable definition in the given language.

    try:
        # List all validity periods.
        api_instance.list_public_validity_periods(variable_definition_id, accept_language)
    except Exception as e:
        print("Exception when calling PublicApi->list_public_validity_periods: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **variable_definition_id** | **str**| Unique identifier for the variable definition. | 
 **accept_language** | [**SupportedLanguages**](.md)| Render the variable definition in the given language. | 

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_public_variable_definitions**
> list_public_variable_definitions(accept_language, date_of_validity=date_of_validity)

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
    api_instance = vardef_client.PublicApi(api_client)
    accept_language = vardef_client.SupportedLanguages() # SupportedLanguages | Render the variable definition in the given language.
    date_of_validity = '' # str | List only variable definitions which are valid on this date. (optional)

    try:
        # List all variable definitions.
        api_instance.list_public_variable_definitions(accept_language, date_of_validity=date_of_validity)
    except Exception as e:
        print("Exception when calling PublicApi->list_public_variable_definitions: %s\n" % e)
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

