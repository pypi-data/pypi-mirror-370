# core.v1.PhysicalGuarantorsApi

All URIs are relative to */v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_physical_guarantors**](PhysicalGuarantorsApi.md#create_physical_guarantors) | **POST** /physical-guarantors | Create physical guarantors
[**delete_physical_guarantors**](PhysicalGuarantorsApi.md#delete_physical_guarantors) | **DELETE** /physical-guarantors/{applicant} | Delete physical guarantors
[**get_physical_guarantors**](PhysicalGuarantorsApi.md#get_physical_guarantors) | **GET** /physical-guarantors/{applicant} | Get physical guarantors
[**list_physical_guarantors**](PhysicalGuarantorsApi.md#list_physical_guarantors) | **GET** /physical-guarantors | List physical guarantors


# **create_physical_guarantors**
> ApisCoreSchemasV1PhysicalGuarantorsPhysicalGuarantor create_physical_guarantors(physical_guarantor_create)

Create physical guarantors

## 🔒 Authentication

This endpoint require a valid OAuth2 Bearer
### Scopes : 
User must provide one of the following scopes:
- `admin`
- `staff`
- `user`
- `org:admin`
- `org:staff`
- `org:user`
- `rental_file:write`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v1
from core.v1.models.apis_core_schemas_v1_physical_guarantors_physical_guarantor import ApisCoreSchemasV1PhysicalGuarantorsPhysicalGuarantor
from core.v1.models.physical_guarantor_create import PhysicalGuarantorCreate
from core.v1.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /v1
# See configuration.py for a list of all supported configuration parameters.
configuration = core.v1.Configuration(
    host = "/v1"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: APIKeyHeader
configuration.api_key['APIKeyHeader'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['APIKeyHeader'] = 'Bearer'

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with core.v1.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = core.v1.PhysicalGuarantorsApi(api_client)
    physical_guarantor_create = core.v1.PhysicalGuarantorCreate() # PhysicalGuarantorCreate | 

    try:
        # Create physical guarantors
        api_response = api_instance.create_physical_guarantors(physical_guarantor_create)
        print("The response of PhysicalGuarantorsApi->create_physical_guarantors:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PhysicalGuarantorsApi->create_physical_guarantors: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **physical_guarantor_create** | [**PhysicalGuarantorCreate**](PhysicalGuarantorCreate.md)|  | 

### Return type

[**ApisCoreSchemasV1PhysicalGuarantorsPhysicalGuarantor**](ApisCoreSchemasV1PhysicalGuarantorsPhysicalGuarantor.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_physical_guarantors**
> delete_physical_guarantors(applicant)

Delete physical guarantors

## 🔒 Authentication

This endpoint require a valid OAuth2 Bearer
### Scopes : 
User must provide one of the following scopes:
- `admin`
- `staff`
- `user`
- `org:admin`
- `org:staff`
- `org:user`
- `rental_file:write`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v1
from core.v1.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /v1
# See configuration.py for a list of all supported configuration parameters.
configuration = core.v1.Configuration(
    host = "/v1"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: APIKeyHeader
configuration.api_key['APIKeyHeader'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['APIKeyHeader'] = 'Bearer'

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with core.v1.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = core.v1.PhysicalGuarantorsApi(api_client)
    applicant = 'applicant_example' # str | 

    try:
        # Delete physical guarantors
        api_instance.delete_physical_guarantors(applicant)
    except Exception as e:
        print("Exception when calling PhysicalGuarantorsApi->delete_physical_guarantors: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **applicant** | **str**|  | 

### Return type

void (empty response body)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_physical_guarantors**
> ApisCoreSchemasV1PhysicalGuarantorsPhysicalGuarantor get_physical_guarantors(applicant)

Get physical guarantors

## 🔒 Authentication

This endpoint require a valid OAuth2 Bearer
### Scopes : 
User must provide one of the following scopes:
- `admin`
- `staff`
- `user`
- `org:admin`
- `org:staff`
- `org:user`
- `rental_file:read`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v1
from core.v1.models.apis_core_schemas_v1_physical_guarantors_physical_guarantor import ApisCoreSchemasV1PhysicalGuarantorsPhysicalGuarantor
from core.v1.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /v1
# See configuration.py for a list of all supported configuration parameters.
configuration = core.v1.Configuration(
    host = "/v1"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: APIKeyHeader
configuration.api_key['APIKeyHeader'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['APIKeyHeader'] = 'Bearer'

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with core.v1.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = core.v1.PhysicalGuarantorsApi(api_client)
    applicant = 'applicant_example' # str | 

    try:
        # Get physical guarantors
        api_response = api_instance.get_physical_guarantors(applicant)
        print("The response of PhysicalGuarantorsApi->get_physical_guarantors:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PhysicalGuarantorsApi->get_physical_guarantors: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **applicant** | **str**|  | 

### Return type

[**ApisCoreSchemasV1PhysicalGuarantorsPhysicalGuarantor**](ApisCoreSchemasV1PhysicalGuarantorsPhysicalGuarantor.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_physical_guarantors**
> PaginatedResponsePhysicalGuarantor list_physical_guarantors(limit=limit, offset=offset)

List physical guarantors

## 🔒 Authentication

This endpoint require a valid OAuth2 Bearer
### Scopes : 
User must provide one of the following scopes:
- `admin`
- `staff`
- `user`
- `org:admin`
- `org:staff`
- `org:user`
- `rental_file:read`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v1
from core.v1.models.paginated_response_physical_guarantor import PaginatedResponsePhysicalGuarantor
from core.v1.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /v1
# See configuration.py for a list of all supported configuration parameters.
configuration = core.v1.Configuration(
    host = "/v1"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: APIKeyHeader
configuration.api_key['APIKeyHeader'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['APIKeyHeader'] = 'Bearer'

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with core.v1.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = core.v1.PhysicalGuarantorsApi(api_client)
    limit = 10 # int |  (optional) (default to 10)
    offset = 0 # int |  (optional) (default to 0)

    try:
        # List physical guarantors
        api_response = api_instance.list_physical_guarantors(limit=limit, offset=offset)
        print("The response of PhysicalGuarantorsApi->list_physical_guarantors:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PhysicalGuarantorsApi->list_physical_guarantors: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**|  | [optional] [default to 10]
 **offset** | **int**|  | [optional] [default to 0]

### Return type

[**PaginatedResponsePhysicalGuarantor**](PaginatedResponsePhysicalGuarantor.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

