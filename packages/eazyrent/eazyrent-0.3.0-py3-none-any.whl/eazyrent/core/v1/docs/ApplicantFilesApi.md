# core.v1.ApplicantFilesApi

All URIs are relative to */v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_applicant_files**](ApplicantFilesApi.md#create_applicant_files) | **POST** /applicant-files | Create applicant files
[**delete_applicant_file**](ApplicantFilesApi.md#delete_applicant_file) | **DELETE** /applicant-files/{id} | Delete applicant file
[**get_applicant_file**](ApplicantFilesApi.md#get_applicant_file) | **GET** /applicant-files/{id} | Get applicant file
[**list_applicant_files**](ApplicantFilesApi.md#list_applicant_files) | **GET** /applicant-files | List applicant files
[**list_full_rental_files**](ApplicantFilesApi.md#list_full_rental_files) | **GET** /applicant-files/full | List full rental files
[**partial_update_applicant_file**](ApplicantFilesApi.md#partial_update_applicant_file) | **PATCH** /applicant-files/{id} | Partial update applicant file
[**update_applicant_file**](ApplicantFilesApi.md#update_applicant_file) | **PUT** /applicant-files/{id} | Update applicant file


# **create_applicant_files**
> RentalFile create_applicant_files(rental_file_create)

Create applicant files

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
from core.v1.models.rental_file import RentalFile
from core.v1.models.rental_file_create import RentalFileCreate
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
    api_instance = core.v1.ApplicantFilesApi(api_client)
    rental_file_create = core.v1.RentalFileCreate() # RentalFileCreate | 

    try:
        # Create applicant files
        api_response = api_instance.create_applicant_files(rental_file_create)
        print("The response of ApplicantFilesApi->create_applicant_files:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ApplicantFilesApi->create_applicant_files: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **rental_file_create** | [**RentalFileCreate**](RentalFileCreate.md)|  | 

### Return type

[**RentalFile**](RentalFile.md)

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

# **delete_applicant_file**
> delete_applicant_file(id)

Delete applicant file

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
    api_instance = core.v1.ApplicantFilesApi(api_client)
    id = 'id_example' # str | 

    try:
        # Delete applicant file
        api_instance.delete_applicant_file(id)
    except Exception as e:
        print("Exception when calling ApplicantFilesApi->delete_applicant_file: %s\n" % e)
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

# **get_applicant_file**
> RentalFile get_applicant_file(id)

Get applicant file

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
from core.v1.models.rental_file import RentalFile
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
    api_instance = core.v1.ApplicantFilesApi(api_client)
    id = 'id_example' # str | 

    try:
        # Get applicant file
        api_response = api_instance.get_applicant_file(id)
        print("The response of ApplicantFilesApi->get_applicant_file:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ApplicantFilesApi->get_applicant_file: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

[**RentalFile**](RentalFile.md)

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

# **list_applicant_files**
> PaginatedResponseRentalFileList list_applicant_files(order_by=order_by, limit=limit, offset=offset, applicants_situation=applicants_situation, property_rent=property_rent, status=status, simple_status=simple_status)

List applicant files

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
from core.v1.models.paginated_response_rental_file_list import PaginatedResponseRentalFileList
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
    api_instance = core.v1.ApplicantFilesApi(api_client)
    order_by = -created_at # str |  (optional) (default to -created_at)
    limit = 10 # int |  (optional) (default to 10)
    offset = 0 # int |  (optional) (default to 0)
    applicants_situation = 'applicants_situation_example' # str |  (optional)
    property_rent = 'property_rent_example' # str |  (optional)
    status = 'status_example' # str |  (optional)
    simple_status = 'simple_status_example' # str |  (optional)

    try:
        # List applicant files
        api_response = api_instance.list_applicant_files(order_by=order_by, limit=limit, offset=offset, applicants_situation=applicants_situation, property_rent=property_rent, status=status, simple_status=simple_status)
        print("The response of ApplicantFilesApi->list_applicant_files:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ApplicantFilesApi->list_applicant_files: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **order_by** | **str**|  | [optional] [default to -created_at]
 **limit** | **int**|  | [optional] [default to 10]
 **offset** | **int**|  | [optional] [default to 0]
 **applicants_situation** | **str**|  | [optional] 
 **property_rent** | **str**|  | [optional] 
 **status** | **str**|  | [optional] 
 **simple_status** | **str**|  | [optional] 

### Return type

[**PaginatedResponseRentalFileList**](PaginatedResponseRentalFileList.md)

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

# **list_full_rental_files**
> PaginatedResponseRentalFileFull list_full_rental_files(order_by=order_by, limit=limit, offset=offset, applicants_situation=applicants_situation, property_rent=property_rent, status=status, simple_status=simple_status)

List full rental files

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
from core.v1.models.paginated_response_rental_file_full import PaginatedResponseRentalFileFull
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
    api_instance = core.v1.ApplicantFilesApi(api_client)
    order_by = -created_at # str |  (optional) (default to -created_at)
    limit = 10 # int |  (optional) (default to 10)
    offset = 0 # int |  (optional) (default to 0)
    applicants_situation = 'applicants_situation_example' # str |  (optional)
    property_rent = 'property_rent_example' # str |  (optional)
    status = 'status_example' # str |  (optional)
    simple_status = 'simple_status_example' # str |  (optional)

    try:
        # List full rental files
        api_response = api_instance.list_full_rental_files(order_by=order_by, limit=limit, offset=offset, applicants_situation=applicants_situation, property_rent=property_rent, status=status, simple_status=simple_status)
        print("The response of ApplicantFilesApi->list_full_rental_files:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ApplicantFilesApi->list_full_rental_files: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **order_by** | **str**|  | [optional] [default to -created_at]
 **limit** | **int**|  | [optional] [default to 10]
 **offset** | **int**|  | [optional] [default to 0]
 **applicants_situation** | **str**|  | [optional] 
 **property_rent** | **str**|  | [optional] 
 **status** | **str**|  | [optional] 
 **simple_status** | **str**|  | [optional] 

### Return type

[**PaginatedResponseRentalFileFull**](PaginatedResponseRentalFileFull.md)

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

# **partial_update_applicant_file**
> RentalFile partial_update_applicant_file(id, rental_file_partial_update)

Partial update applicant file

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
from core.v1.models.rental_file import RentalFile
from core.v1.models.rental_file_partial_update import RentalFilePartialUpdate
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
    api_instance = core.v1.ApplicantFilesApi(api_client)
    id = 'id_example' # str | 
    rental_file_partial_update = core.v1.RentalFilePartialUpdate() # RentalFilePartialUpdate | 

    try:
        # Partial update applicant file
        api_response = api_instance.partial_update_applicant_file(id, rental_file_partial_update)
        print("The response of ApplicantFilesApi->partial_update_applicant_file:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ApplicantFilesApi->partial_update_applicant_file: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **rental_file_partial_update** | [**RentalFilePartialUpdate**](RentalFilePartialUpdate.md)|  | 

### Return type

[**RentalFile**](RentalFile.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_applicant_file**
> RentalFile update_applicant_file(id, rental_file_create)

Update applicant file

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
from core.v1.models.rental_file import RentalFile
from core.v1.models.rental_file_create import RentalFileCreate
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
    api_instance = core.v1.ApplicantFilesApi(api_client)
    id = 'id_example' # str | 
    rental_file_create = core.v1.RentalFileCreate() # RentalFileCreate | 

    try:
        # Update applicant file
        api_response = api_instance.update_applicant_file(id, rental_file_create)
        print("The response of ApplicantFilesApi->update_applicant_file:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ApplicantFilesApi->update_applicant_file: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **rental_file_create** | [**RentalFileCreate**](RentalFileCreate.md)|  | 

### Return type

[**RentalFile**](RentalFile.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

