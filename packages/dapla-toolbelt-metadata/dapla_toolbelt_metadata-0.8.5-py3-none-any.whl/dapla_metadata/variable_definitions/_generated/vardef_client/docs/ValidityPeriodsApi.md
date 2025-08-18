# vardef_client.ValidityPeriodsApi

All URIs are relative to *https://metadata.intern.test.ssb.no*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_validity_period**](ValidityPeriodsApi.md#create_validity_period) | **POST** /variable-definitions/{variable-definition-id}/validity-periods | Create a new validity period for a variable definition.
[**list_public_validity_periods_0**](ValidityPeriodsApi.md#list_public_validity_periods_0) | **GET** /public/variable-definitions/{variable-definition-id}/validity-periods | List all validity periods.
[**list_validity_periods**](ValidityPeriodsApi.md#list_validity_periods) | **GET** /variable-definitions/{variable-definition-id}/validity-periods | List all validity periods.


# **create_validity_period**
> create_validity_period(variable_definition_id, active_group, validity_period)

Create a new validity period for a variable definition.

Create a new validity period for a variable definition.

### Example

* Bearer (JWT) Authentication (Keycloak token):

```python
import vardef_client
from vardef_client.models.validity_period import ValidityPeriod
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
    api_instance = vardef_client.ValidityPeriodsApi(api_client)
    variable_definition_id = 'wypvb3wd' # str | Unique identifier for the variable definition.
    active_group = 'dapla-felles-developers' # str | The group which the user currently represents.
    validity_period = vardef_client.ValidityPeriod() # ValidityPeriod | 

    try:
        # Create a new validity period for a variable definition.
        api_instance.create_validity_period(variable_definition_id, active_group, validity_period)
    except Exception as e:
        print("Exception when calling ValidityPeriodsApi->create_validity_period: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **variable_definition_id** | **str**| Unique identifier for the variable definition. | 
 **active_group** | **str**| The group which the user currently represents. | 
 **validity_period** | [**ValidityPeriod**](ValidityPeriod.md)|  | 

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
**400** | The request is missing or has errors in required fields. |  -  |
**405** | Method only allowed for published variables. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_public_validity_periods_0**
> list_public_validity_periods_0(variable_definition_id, accept_language)

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
    api_instance = vardef_client.ValidityPeriodsApi(api_client)
    variable_definition_id = 'wypvb3wd' # str | Unique identifier for the variable definition.
    accept_language = vardef_client.SupportedLanguages() # SupportedLanguages | Render the variable definition in the given language.

    try:
        # List all validity periods.
        api_instance.list_public_validity_periods_0(variable_definition_id, accept_language)
    except Exception as e:
        print("Exception when calling ValidityPeriodsApi->list_public_validity_periods_0: %s\n" % e)
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

# **list_validity_periods**
> list_validity_periods(variable_definition_id)

List all validity periods.

List all validity periods.

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
    api_instance = vardef_client.ValidityPeriodsApi(api_client)
    variable_definition_id = 'wypvb3wd' # str | Unique identifier for the variable definition.

    try:
        # List all validity periods.
        api_instance.list_validity_periods(variable_definition_id)
    except Exception as e:
        print("Exception when calling ValidityPeriodsApi->list_validity_periods: %s\n" % e)
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
**200** | Ok |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

