# core.v1.RentsApi

All URIs are relative to */v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**bulk_import**](RentsApi.md#bulk_import) | **POST** /rents/bulk-import | Bulk import
[**create_rent**](RentsApi.md#create_rent) | **POST** /rents | Create rent
[**delete_rent**](RentsApi.md#delete_rent) | **DELETE** /rents/{id} | Delete rent
[**get_rent**](RentsApi.md#get_rent) | **GET** /rents/{id} | Get rent
[**list_rents**](RentsApi.md#list_rents) | **GET** /rents | List rents
[**partial_update_rent**](RentsApi.md#partial_update_rent) | **PATCH** /rents/{id} | Partial update rent
[**update_rent**](RentsApi.md#update_rent) | **PUT** /rents/{id} | Update rent


# **bulk_import**
> object bulk_import(parser, file)

Bulk import

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
- `product:write`

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
    api_instance = core.v1.RentsApi(api_client)
    parser = 'parser_example' # str | 
    file = None # bytearray | 

    try:
        # Bulk import
        api_response = api_instance.bulk_import(parser, file)
        print("The response of RentsApi->bulk_import:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RentsApi->bulk_import: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **parser** | **str**|  | 
 **file** | **bytearray**|  | 

### Return type

**object**

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_rent**
> PropertyRent create_rent(property_rent_create)

Create rent

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
- `product:write`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v1
from core.v1.models.property_rent import PropertyRent
from core.v1.models.property_rent_create import PropertyRentCreate
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
    api_instance = core.v1.RentsApi(api_client)
    property_rent_create = core.v1.PropertyRentCreate() # PropertyRentCreate | 

    try:
        # Create rent
        api_response = api_instance.create_rent(property_rent_create)
        print("The response of RentsApi->create_rent:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RentsApi->create_rent: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **property_rent_create** | [**PropertyRentCreate**](PropertyRentCreate.md)|  | 

### Return type

[**PropertyRent**](PropertyRent.md)

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

# **delete_rent**
> delete_rent(id)

Delete rent

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
- `product:write`

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
    api_instance = core.v1.RentsApi(api_client)
    id = 'id_example' # str | 

    try:
        # Delete rent
        api_instance.delete_rent(id)
    except Exception as e:
        print("Exception when calling RentsApi->delete_rent: %s\n" % e)
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

# **get_rent**
> PropertyRent get_rent(id)

Get rent

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
- `product:read`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v1
from core.v1.models.property_rent import PropertyRent
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
    api_instance = core.v1.RentsApi(api_client)
    id = 'id_example' # str | 

    try:
        # Get rent
        api_response = api_instance.get_rent(id)
        print("The response of RentsApi->get_rent:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RentsApi->get_rent: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

[**PropertyRent**](PropertyRent.md)

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

# **list_rents**
> PaginatedResponsePropertyRentList list_rents(order_by=order_by, limit=limit, offset=offset, reference=reference, search=search)

List rents

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
- `product:read`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v1
from core.v1.models.paginated_response_property_rent_list import PaginatedResponsePropertyRentList
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
    api_instance = core.v1.RentsApi(api_client)
    order_by = -created_at # str |  (optional) (default to -created_at)
    limit = 10 # int |  (optional) (default to 10)
    offset = 0 # int |  (optional) (default to 0)
    reference = 'reference_example' # str |  (optional)
    search = 'search_example' # str |  (optional)

    try:
        # List rents
        api_response = api_instance.list_rents(order_by=order_by, limit=limit, offset=offset, reference=reference, search=search)
        print("The response of RentsApi->list_rents:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RentsApi->list_rents: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **order_by** | **str**|  | [optional] [default to -created_at]
 **limit** | **int**|  | [optional] [default to 10]
 **offset** | **int**|  | [optional] [default to 0]
 **reference** | **str**|  | [optional] 
 **search** | **str**|  | [optional] 

### Return type

[**PaginatedResponsePropertyRentList**](PaginatedResponsePropertyRentList.md)

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

# **partial_update_rent**
> PropertyRentPartialUpdate partial_update_rent(id, property_rent_partial_update)

Partial update rent

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
- `product:write`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v1
from core.v1.models.property_rent_partial_update import PropertyRentPartialUpdate
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
    api_instance = core.v1.RentsApi(api_client)
    id = 'id_example' # str | 
    property_rent_partial_update = core.v1.PropertyRentPartialUpdate() # PropertyRentPartialUpdate | 

    try:
        # Partial update rent
        api_response = api_instance.partial_update_rent(id, property_rent_partial_update)
        print("The response of RentsApi->partial_update_rent:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RentsApi->partial_update_rent: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **property_rent_partial_update** | [**PropertyRentPartialUpdate**](PropertyRentPartialUpdate.md)|  | 

### Return type

[**PropertyRentPartialUpdate**](PropertyRentPartialUpdate.md)

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

# **update_rent**
> PropertyRentCreate update_rent(id, property_rent_create)

Update rent

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
- `product:write`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v1
from core.v1.models.property_rent_create import PropertyRentCreate
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
    api_instance = core.v1.RentsApi(api_client)
    id = 'id_example' # str | 
    property_rent_create = core.v1.PropertyRentCreate() # PropertyRentCreate | 

    try:
        # Update rent
        api_response = api_instance.update_rent(id, property_rent_create)
        print("The response of RentsApi->update_rent:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RentsApi->update_rent: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **property_rent_create** | [**PropertyRentCreate**](PropertyRentCreate.md)|  | 

### Return type

[**PropertyRentCreate**](PropertyRentCreate.md)

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

