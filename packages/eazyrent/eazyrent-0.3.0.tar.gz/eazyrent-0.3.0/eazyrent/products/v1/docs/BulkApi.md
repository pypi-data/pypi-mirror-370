# products.v1.BulkApi

All URIs are relative to */products/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**bulk_import**](BulkApi.md#bulk_import) | **POST** /bulk/ | Bulk import
[**bulk_import_from_s3**](BulkApi.md#bulk_import_from_s3) | **POST** /bulk/s3/ | Bulk import from s3
[**export_products**](BulkApi.md#export_products) | **POST** /bulk/export/ | Export products
[**validate_descriptor**](BulkApi.md#validate_descriptor) | **POST** /bulk/validate-descriptor/ | Validate descriptor
[**validate_import**](BulkApi.md#validate_import) | **POST** /bulk/validate/ | Validate import


# **bulk_import**
> object bulk_import(file, descriptor, x_eaz_account_id=x_eaz_account_id)

Bulk import

Import products from file.

file: The file that contains products to import
descriptor: yaml file that contains description of the file.

## 🔒 Authentication

This endpoint require a valid OAuth2 Bearer

It supports account impersonation within Organization's
sub-accounts using `X-Eaz-Account-Id` Header.

- If the `X-Eaz-Account-Id` header is provided and the user has access rights
to that sub-account, the impersonation context is applied.
- Otherwise, the user's own account context is used.
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
import products.v1
from products.v1.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /products/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = products.v1.Configuration(
    host = "/products/v1"
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
with products.v1.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = products.v1.BulkApi(api_client)
    file = None # bytearray | 
    descriptor = None # bytearray | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Bulk import
        api_response = api_instance.bulk_import(file, descriptor, x_eaz_account_id=x_eaz_account_id)
        print("The response of BulkApi->bulk_import:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BulkApi->bulk_import: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file** | **bytearray**|  | 
 **descriptor** | **bytearray**|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

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
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **bulk_import_from_s3**
> object bulk_import_from_s3(file_path, descriptor, x_eaz_account_id=x_eaz_account_id)

Bulk import from s3

Import products from file.

file: The file that contains products to import
descriptor: yaml file that contains description of the file.

## 🔒 Authentication

This endpoint require a valid OAuth2 Bearer

It supports account impersonation within Organization's
sub-accounts using `X-Eaz-Account-Id` Header.

- If the `X-Eaz-Account-Id` header is provided and the user has access rights
to that sub-account, the impersonation context is applied.
- Otherwise, the user's own account context is used.
### Scopes : 
User must provide one of the following scopes:
- `admin`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import products.v1
from products.v1.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /products/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = products.v1.Configuration(
    host = "/products/v1"
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
with products.v1.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = products.v1.BulkApi(api_client)
    file_path = 'file_path_example' # str | 
    descriptor = None # bytearray | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Bulk import from s3
        api_response = api_instance.bulk_import_from_s3(file_path, descriptor, x_eaz_account_id=x_eaz_account_id)
        print("The response of BulkApi->bulk_import_from_s3:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BulkApi->bulk_import_from_s3: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_path** | **str**|  | 
 **descriptor** | **bytearray**|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

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
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **export_products**
> object export_products(x_eaz_account_id=x_eaz_account_id)

Export products

## 🔒 Authentication

This endpoint require a valid OAuth2 Bearer

It supports account impersonation within Organization's
sub-accounts using `X-Eaz-Account-Id` Header.

- If the `X-Eaz-Account-Id` header is provided and the user has access rights
to that sub-account, the impersonation context is applied.
- Otherwise, the user's own account context is used.
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
import products.v1
from products.v1.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /products/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = products.v1.Configuration(
    host = "/products/v1"
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
with products.v1.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = products.v1.BulkApi(api_client)
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Export products
        api_response = api_instance.export_products(x_eaz_account_id=x_eaz_account_id)
        print("The response of BulkApi->export_products:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BulkApi->export_products: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

**object**

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

# **validate_descriptor**
> ResponseValidateDescriptor validate_descriptor(descriptor, x_eaz_account_id=x_eaz_account_id)

Validate descriptor

## 🔒 Authentication

This endpoint require a valid OAuth2 Bearer

It supports account impersonation within Organization's
sub-accounts using `X-Eaz-Account-Id` Header.

- If the `X-Eaz-Account-Id` header is provided and the user has access rights
to that sub-account, the impersonation context is applied.
- Otherwise, the user's own account context is used.
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
import products.v1
from products.v1.models.response_validate_descriptor import ResponseValidateDescriptor
from products.v1.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /products/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = products.v1.Configuration(
    host = "/products/v1"
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
with products.v1.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = products.v1.BulkApi(api_client)
    descriptor = None # bytearray | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Validate descriptor
        api_response = api_instance.validate_descriptor(descriptor, x_eaz_account_id=x_eaz_account_id)
        print("The response of BulkApi->validate_descriptor:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BulkApi->validate_descriptor: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **descriptor** | **bytearray**|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

[**ResponseValidateDescriptor**](ResponseValidateDescriptor.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **validate_import**
> List[ValidateImport200ResponseInner] validate_import(file, descriptor, x_eaz_account_id=x_eaz_account_id)

Validate import

Validate file against descriptor
this is a dry mode.

## 🔒 Authentication

This endpoint require a valid OAuth2 Bearer

It supports account impersonation within Organization's
sub-accounts using `X-Eaz-Account-Id` Header.

- If the `X-Eaz-Account-Id` header is provided and the user has access rights
to that sub-account, the impersonation context is applied.
- Otherwise, the user's own account context is used.
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
import products.v1
from products.v1.models.validate_import200_response_inner import ValidateImport200ResponseInner
from products.v1.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /products/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = products.v1.Configuration(
    host = "/products/v1"
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
with products.v1.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = products.v1.BulkApi(api_client)
    file = None # bytearray | 
    descriptor = None # bytearray | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Validate import
        api_response = api_instance.validate_import(file, descriptor, x_eaz_account_id=x_eaz_account_id)
        print("The response of BulkApi->validate_import:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BulkApi->validate_import: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file** | **bytearray**|  | 
 **descriptor** | **bytearray**|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

[**List[ValidateImport200ResponseInner]**](ValidateImport200ResponseInner.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

