# core.v1.ApplicantsApi

All URIs are relative to */v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_applicant**](ApplicantsApi.md#create_applicant) | **POST** /applicants | Create applicant
[**delete_applicant**](ApplicantsApi.md#delete_applicant) | **DELETE** /applicants/{id} | Delete applicant
[**get_applicant**](ApplicantsApi.md#get_applicant) | **GET** /applicants/{id} | Get applicant
[**list_applicants**](ApplicantsApi.md#list_applicants) | **GET** /applicants | List applicants


# **create_applicant**
> Applicant create_applicant(create_applicant)

Create applicant

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
from core.v1.models.applicant import Applicant
from core.v1.models.create_applicant import CreateApplicant
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
    api_instance = core.v1.ApplicantsApi(api_client)
    create_applicant = core.v1.CreateApplicant() # CreateApplicant | 

    try:
        # Create applicant
        api_response = api_instance.create_applicant(create_applicant)
        print("The response of ApplicantsApi->create_applicant:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ApplicantsApi->create_applicant: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_applicant** | [**CreateApplicant**](CreateApplicant.md)|  | 

### Return type

[**Applicant**](Applicant.md)

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

# **delete_applicant**
> delete_applicant(id)

Delete applicant

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
    api_instance = core.v1.ApplicantsApi(api_client)
    id = 'id_example' # str | 

    try:
        # Delete applicant
        api_instance.delete_applicant(id)
    except Exception as e:
        print("Exception when calling ApplicantsApi->delete_applicant: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

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

# **get_applicant**
> Applicant get_applicant(id)

Get applicant

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
from core.v1.models.applicant import Applicant
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
    api_instance = core.v1.ApplicantsApi(api_client)
    id = 'id_example' # str | 

    try:
        # Get applicant
        api_response = api_instance.get_applicant(id)
        print("The response of ApplicantsApi->get_applicant:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ApplicantsApi->get_applicant: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

[**Applicant**](Applicant.md)

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

# **list_applicants**
> PaginatedResponseApplicantList list_applicants(order_by=order_by, limit=limit, offset=offset, applicant_file=applicant_file, applicant_file_reference=applicant_file_reference, is_guarantor=is_guarantor, search=search, simple_status=simple_status, status=status, submitted=submitted)

List applicants

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
from core.v1.models.paginated_response_applicant_list import PaginatedResponseApplicantList
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
    api_instance = core.v1.ApplicantsApi(api_client)
    order_by = -created_at # str |  (optional) (default to -created_at)
    limit = 10 # int |  (optional) (default to 10)
    offset = 0 # int |  (optional) (default to 0)
    applicant_file = 'applicant_file_example' # str |  (optional)
    applicant_file_reference = 'applicant_file_reference_example' # str |  (optional)
    is_guarantor = True # bool |  (optional)
    search = 'search_example' # str |  (optional)
    simple_status = 'simple_status_example' # str |  (optional)
    status = 'status_example' # str |  (optional)
    submitted = True # bool |  (optional)

    try:
        # List applicants
        api_response = api_instance.list_applicants(order_by=order_by, limit=limit, offset=offset, applicant_file=applicant_file, applicant_file_reference=applicant_file_reference, is_guarantor=is_guarantor, search=search, simple_status=simple_status, status=status, submitted=submitted)
        print("The response of ApplicantsApi->list_applicants:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ApplicantsApi->list_applicants: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **order_by** | **str**|  | [optional] [default to -created_at]
 **limit** | **int**|  | [optional] [default to 10]
 **offset** | **int**|  | [optional] [default to 0]
 **applicant_file** | **str**|  | [optional] 
 **applicant_file_reference** | **str**|  | [optional] 
 **is_guarantor** | **bool**|  | [optional] 
 **search** | **str**|  | [optional] 
 **simple_status** | **str**|  | [optional] 
 **status** | **str**|  | [optional] 
 **submitted** | **bool**|  | [optional] 

### Return type

[**PaginatedResponseApplicantList**](PaginatedResponseApplicantList.md)

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

