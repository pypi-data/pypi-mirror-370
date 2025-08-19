# core.v2.RentalFilesApi

All URIs are relative to */v2*

Method | HTTP request | Description
------------- | ------------- | -------------
[**ask_analysis**](RentalFilesApi.md#ask_analysis) | **POST** /rental-files/{id}/ask-analysis/ | Ask analysis
[**close_rental_file**](RentalFilesApi.md#close_rental_file) | **POST** /rental-files/{id}/close/ | Close rental file
[**create_rental_file**](RentalFilesApi.md#create_rental_file) | **POST** /rental-files/ | Create rental file
[**delete_rental_file**](RentalFilesApi.md#delete_rental_file) | **DELETE** /rental-files/{id}/ | Delete rental file
[**download_documents**](RentalFilesApi.md#download_documents) | **GET** /rental-files/{id}/download/ | Download documents
[**get_analysis_report**](RentalFilesApi.md#get_analysis_report) | **GET** /rental-files/{id}/report/ | Get analysis report
[**get_rental_file**](RentalFilesApi.md#get_rental_file) | **GET** /rental-files/{id}/ | Get rental file
[**get_rental_file_by_metadata**](RentalFilesApi.md#get_rental_file_by_metadata) | **GET** /rental-files/resolve/ | Get rental file by metadata
[**get_rental_file_history_events**](RentalFilesApi.md#get_rental_file_history_events) | **GET** /rental-files/{id}/history | Get rental file history events
[**get_rental_file_status**](RentalFilesApi.md#get_rental_file_status) | **GET** /rental-files/{id}/status/ | Get rental file status
[**get_rental_file_status_by_metadata**](RentalFilesApi.md#get_rental_file_status_by_metadata) | **GET** /rental-files/resolve/status/ | Get rental file status by metadata
[**invite_applicant**](RentalFilesApi.md#invite_applicant) | **POST** /rental-files/invite/ | Invite applicant
[**list_rental_files**](RentalFilesApi.md#list_rental_files) | **GET** /rental-files/ | List rental files
[**lock_applicant_form**](RentalFilesApi.md#lock_applicant_form) | **POST** /rental-files/{applicant_id}/lock-form/ | Lock applicant form
[**partial_update_rental_file**](RentalFilesApi.md#partial_update_rental_file) | **PATCH** /rental-files/{id}/ | Partial update rental file
[**reopen_all_forms**](RentalFilesApi.md#reopen_all_forms) | **POST** /rental-files/{id}/unlock-forms/ | Reopen all forms
[**reopen_applicant_form**](RentalFilesApi.md#reopen_applicant_form) | **POST** /rental-files/{applicant_id}/unlock-form/ | Reopen applicant form
[**update_rental_file**](RentalFilesApi.md#update_rental_file) | **PUT** /rental-files/{id}/ | Update rental file
[**validate_pre_application**](RentalFilesApi.md#validate_pre_application) | **POST** /rental-files/{id}/validate-pre-application/ | Validate pre application


# **ask_analysis**
> object ask_analysis(id, x_eaz_account_id=x_eaz_account_id)

Ask analysis

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
- `rental_file:write`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v2
from core.v2.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /v2
# See configuration.py for a list of all supported configuration parameters.
configuration = core.v2.Configuration(
    host = "/v2"
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
with core.v2.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = core.v2.RentalFilesApi(api_client)
    id = 'id_example' # str | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Ask analysis
        api_response = api_instance.ask_analysis(id, x_eaz_account_id=x_eaz_account_id)
        print("The response of RentalFilesApi->ask_analysis:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RentalFilesApi->ask_analysis: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
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
**202** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **close_rental_file**
> object close_rental_file(id, close_rental_file, x_eaz_account_id=x_eaz_account_id)

Close rental file

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
- `rental_file:write`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v2
from core.v2.models.close_rental_file import CloseRentalFile
from core.v2.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /v2
# See configuration.py for a list of all supported configuration parameters.
configuration = core.v2.Configuration(
    host = "/v2"
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
with core.v2.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = core.v2.RentalFilesApi(api_client)
    id = 'id_example' # str | 
    close_rental_file = core.v2.CloseRentalFile() # CloseRentalFile | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Close rental file
        api_response = api_instance.close_rental_file(id, close_rental_file, x_eaz_account_id=x_eaz_account_id)
        print("The response of RentalFilesApi->close_rental_file:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RentalFilesApi->close_rental_file: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **close_rental_file** | [**CloseRentalFile**](CloseRentalFile.md)|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

**object**

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_rental_file**
> RentalFile create_rental_file(create_rental_file, x_eaz_account_id=x_eaz_account_id)

Create rental file

Create a Rental File.

This endpoint allows the authenticated user to create a new rental file
associated with their organization. The rental file details must be provided
in the request body.

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
- `rental_file:write`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v2
from core.v2.models.create_rental_file import CreateRentalFile
from core.v2.models.rental_file import RentalFile
from core.v2.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /v2
# See configuration.py for a list of all supported configuration parameters.
configuration = core.v2.Configuration(
    host = "/v2"
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
with core.v2.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = core.v2.RentalFilesApi(api_client)
    create_rental_file = core.v2.CreateRentalFile() # CreateRentalFile | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Create rental file
        api_response = api_instance.create_rental_file(create_rental_file, x_eaz_account_id=x_eaz_account_id)
        print("The response of RentalFilesApi->create_rental_file:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RentalFilesApi->create_rental_file: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_rental_file** | [**CreateRentalFile**](CreateRentalFile.md)|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

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

# **delete_rental_file**
> delete_rental_file(id, x_eaz_account_id=x_eaz_account_id)

Delete rental file

Delete a Rental File by ID.

This endpoint allows the authenticated user to delete a specific rental
file using its unique identifier. If the operation is successful,
a 204 No Content response will be returned.

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
- `rental_file:write`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v2
from core.v2.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /v2
# See configuration.py for a list of all supported configuration parameters.
configuration = core.v2.Configuration(
    host = "/v2"
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
with core.v2.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = core.v2.RentalFilesApi(api_client)
    id = 'id_example' # str | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Delete rental file
        api_instance.delete_rental_file(id, x_eaz_account_id=x_eaz_account_id)
    except Exception as e:
        print("Exception when calling RentalFilesApi->delete_rental_file: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

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

# **download_documents**
> object download_documents(id, format=format, x_eaz_account_id=x_eaz_account_id)

Download documents

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
- `rental_file:read`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v2
from core.v2.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /v2
# See configuration.py for a list of all supported configuration parameters.
configuration = core.v2.Configuration(
    host = "/v2"
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
with core.v2.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = core.v2.RentalFilesApi(api_client)
    id = 'id_example' # str | 
    format = pdf # str |  (optional) (default to pdf)
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Download documents
        api_response = api_instance.download_documents(id, format=format, x_eaz_account_id=x_eaz_account_id)
        print("The response of RentalFilesApi->download_documents:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RentalFilesApi->download_documents: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **format** | **str**|  | [optional] [default to pdf]
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

# **get_analysis_report**
> object get_analysis_report(id, x_eaz_account_id=x_eaz_account_id)

Get analysis report

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
- `rental_file:read`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v2
from core.v2.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /v2
# See configuration.py for a list of all supported configuration parameters.
configuration = core.v2.Configuration(
    host = "/v2"
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
with core.v2.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = core.v2.RentalFilesApi(api_client)
    id = 'id_example' # str | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Get analysis report
        api_response = api_instance.get_analysis_report(id, x_eaz_account_id=x_eaz_account_id)
        print("The response of RentalFilesApi->get_analysis_report:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RentalFilesApi->get_analysis_report: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
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

# **get_rental_file**
> RentalFile get_rental_file(id, x_eaz_account_id=x_eaz_account_id)

Get rental file

Retrieve a Rental File by ID.

This endpoint allows the authenticated user to retrieve the details of a
specific rental file using its unique identifier. The user must have the
necessary permissions to access this information.

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
- `rental_file:read`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v2
from core.v2.models.rental_file import RentalFile
from core.v2.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /v2
# See configuration.py for a list of all supported configuration parameters.
configuration = core.v2.Configuration(
    host = "/v2"
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
with core.v2.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = core.v2.RentalFilesApi(api_client)
    id = 'id_example' # str | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Get rental file
        api_response = api_instance.get_rental_file(id, x_eaz_account_id=x_eaz_account_id)
        print("The response of RentalFilesApi->get_rental_file:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RentalFilesApi->get_rental_file: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

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

# **get_rental_file_by_metadata**
> RentalFile get_rental_file_by_metadata(meta_key, meta_value, x_eaz_account_id=x_eaz_account_id)

Get rental file by metadata

Retrieve a rental file by its metadata key and value.

This endpoint allows clients to fetch a single rental file within their tenant
based on a metadata field. It supports dot-notation for nested fields, enabling
queries on sub-keys (e.g., `internal_data.id`).

Example:

A rental file with the following metadata:

```json
{
    "internals": {
        "id": "12343",
        "reference": "AZXZ1"
    }
}
```

Can be retrieved by:

```
GET /get-by-metadata/?meta_key=internals.id&meta_value=12343
```

or

```
GET /get-by-metadata/?meta_key=internals.id&meta_value=AZXZ1
```

:::warning
    Our system doesn't enforce the uniqueness of your IDs. In case of
    duplicated objects that match your query, **only one** will be returned.
:::

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
- `rental_file:read`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v2
from core.v2.models.rental_file import RentalFile
from core.v2.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /v2
# See configuration.py for a list of all supported configuration parameters.
configuration = core.v2.Configuration(
    host = "/v2"
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
with core.v2.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = core.v2.RentalFilesApi(api_client)
    meta_key = 'meta_key_example' # str | 
    meta_value = 'meta_value_example' # str | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Get rental file by metadata
        api_response = api_instance.get_rental_file_by_metadata(meta_key, meta_value, x_eaz_account_id=x_eaz_account_id)
        print("The response of RentalFilesApi->get_rental_file_by_metadata:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RentalFilesApi->get_rental_file_by_metadata: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **meta_key** | **str**|  | 
 **meta_value** | **str**|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

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

# **get_rental_file_history_events**
> List[HistoryEvent] get_rental_file_history_events(id, x_eaz_account_id=x_eaz_account_id)

Get rental file history events

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
- `rental_file:read`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v2
from core.v2.models.history_event import HistoryEvent
from core.v2.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /v2
# See configuration.py for a list of all supported configuration parameters.
configuration = core.v2.Configuration(
    host = "/v2"
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
with core.v2.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = core.v2.RentalFilesApi(api_client)
    id = 'id_example' # str | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Get rental file history events
        api_response = api_instance.get_rental_file_history_events(id, x_eaz_account_id=x_eaz_account_id)
        print("The response of RentalFilesApi->get_rental_file_history_events:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RentalFilesApi->get_rental_file_history_events: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

[**List[HistoryEvent]**](HistoryEvent.md)

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

# **get_rental_file_status**
> RentalFileStatus get_rental_file_status(id, x_eaz_account_id=x_eaz_account_id)

Get rental file status

Retrieve only the status of a rental file by its ID.

This lightweight endpoint is optimized for performance and environmental impact:
- **Reduced Data Transfer**: Only the status field is returned, minimizing
    network bandwidth usage.
- **Faster Responses**: Projecting a minimal subset of fields accelerates
    database queries and response times.
- **Lower Resource Consumption**: Smaller payloads and quicker operations reduce
    server CPU and memory usage, leading to lower energy consumption.

By isolating status retrieval from the full rental file data, clients can
efficiently poll without incurring the cost of loading the entire document.

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
- `rental_file:read`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v2
from core.v2.models.rental_file_status import RentalFileStatus
from core.v2.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /v2
# See configuration.py for a list of all supported configuration parameters.
configuration = core.v2.Configuration(
    host = "/v2"
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
with core.v2.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = core.v2.RentalFilesApi(api_client)
    id = 'id_example' # str | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Get rental file status
        api_response = api_instance.get_rental_file_status(id, x_eaz_account_id=x_eaz_account_id)
        print("The response of RentalFilesApi->get_rental_file_status:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RentalFilesApi->get_rental_file_status: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

[**RentalFileStatus**](RentalFileStatus.md)

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

# **get_rental_file_status_by_metadata**
> RentalFileStatus get_rental_file_status_by_metadata(meta_key, meta_value, x_eaz_account_id=x_eaz_account_id)

Get rental file status by metadata

Retrieve only the status of a rental file by its metadata key and value.

This lightweight endpoint is optimized for performance and environmental impact:
- **Reduced Data Transfer**: Only the status field is returned, minimizing
    network bandwidth usage.
- **Faster Responses**: Projecting a minimal subset of fields accelerates
    database queries and response times.
- **Lower Resource Consumption**: Smaller payloads and quicker operations reduce
    server CPU and memory usage, leading to lower energy consumption.

By isolating status retrieval from the full rental file data, clients can
efficiently poll without incurring the cost of loading the entire document.

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
- `rental_file:read`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v2
from core.v2.models.rental_file_status import RentalFileStatus
from core.v2.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /v2
# See configuration.py for a list of all supported configuration parameters.
configuration = core.v2.Configuration(
    host = "/v2"
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
with core.v2.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = core.v2.RentalFilesApi(api_client)
    meta_key = 'meta_key_example' # str | 
    meta_value = 'meta_value_example' # str | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Get rental file status by metadata
        api_response = api_instance.get_rental_file_status_by_metadata(meta_key, meta_value, x_eaz_account_id=x_eaz_account_id)
        print("The response of RentalFilesApi->get_rental_file_status_by_metadata:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RentalFilesApi->get_rental_file_status_by_metadata: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **meta_key** | **str**|  | 
 **meta_value** | **str**|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

[**RentalFileStatus**](RentalFileStatus.md)

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

# **invite_applicant**
> RentalFile invite_applicant(invite_payload, x_eaz_account_id=x_eaz_account_id)

Invite applicant

Invite an Applicant for a Rental File.

This endpoint allows the authenticated user to invite an applicant to
apply for a specific rental file. An invitation will be sent to the
applicant's email, allowing them to access and submit their application.

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
- `rental_file:write`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v2
from core.v2.models.invite_payload import InvitePayload
from core.v2.models.rental_file import RentalFile
from core.v2.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /v2
# See configuration.py for a list of all supported configuration parameters.
configuration = core.v2.Configuration(
    host = "/v2"
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
with core.v2.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = core.v2.RentalFilesApi(api_client)
    invite_payload = core.v2.InvitePayload() # InvitePayload | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Invite applicant
        api_response = api_instance.invite_applicant(invite_payload, x_eaz_account_id=x_eaz_account_id)
        print("The response of RentalFilesApi->invite_applicant:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RentalFilesApi->invite_applicant: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **invite_payload** | [**InvitePayload**](InvitePayload.md)|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

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

# **list_rental_files**
> PaginatedResponseListRentalFile list_rental_files(order_by=order_by, limit=limit, offset=offset, search=search, product_id=product_id, managers__in=managers__in, managers__nin=managers__nin, managers__eq=managers__eq, tags__in=tags__in, tags__nin=tags__nin, tags__eq=tags__eq, created_at__lte=created_at__lte, created_at__gte=created_at__gte, updated_at__lte=updated_at__lte, updated_at__gte=updated_at__gte, applicants_situation=applicants_situation, status=status, decision=decision, archived=archived, pre_application_validated=pre_application_validated, x_eaz_account_id=x_eaz_account_id)

List rental files

List Rental Files.

This endpoint allows the authenticated user to retrieve a paginated list of
rental files associated with their organization. Users can apply filters
to refine the results based on specific criteria.

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
- `rental_file:read`

## 📄 Pagination

This endpoint uses pagination with `limit` and `offset`.

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v2
from core.v2.models.paginated_response_list_rental_file import PaginatedResponseListRentalFile
from core.v2.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /v2
# See configuration.py for a list of all supported configuration parameters.
configuration = core.v2.Configuration(
    host = "/v2"
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
with core.v2.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = core.v2.RentalFilesApi(api_client)
    order_by = -created_at # str |  (optional) (default to -created_at)
    limit = 10 # int |  (optional) (default to 10)
    offset = 0 # int |  (optional) (default to 0)
    search = 'search_example' # str |  (optional)
    product_id = 'product_id_example' # str |  (optional)
    managers__in = 'managers__in_example' # str |  (optional)
    managers__nin = 'managers__nin_example' # str |  (optional)
    managers__eq = core.v2.ManagersEq() # ManagersEq |  (optional)
    tags__in = 'tags__in_example' # str |  (optional)
    tags__nin = 'tags__nin_example' # str |  (optional)
    tags__eq = 'tags__eq_example' # str |  (optional)
    created_at__lte = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    created_at__gte = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    updated_at__lte = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    updated_at__gte = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    applicants_situation = 'applicants_situation_example' # str |  (optional)
    status = 'status_example' # str |  (optional)
    decision = 'decision_example' # str |  (optional)
    archived = True # bool |  (optional)
    pre_application_validated = True # bool |  (optional)
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # List rental files
        api_response = api_instance.list_rental_files(order_by=order_by, limit=limit, offset=offset, search=search, product_id=product_id, managers__in=managers__in, managers__nin=managers__nin, managers__eq=managers__eq, tags__in=tags__in, tags__nin=tags__nin, tags__eq=tags__eq, created_at__lte=created_at__lte, created_at__gte=created_at__gte, updated_at__lte=updated_at__lte, updated_at__gte=updated_at__gte, applicants_situation=applicants_situation, status=status, decision=decision, archived=archived, pre_application_validated=pre_application_validated, x_eaz_account_id=x_eaz_account_id)
        print("The response of RentalFilesApi->list_rental_files:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RentalFilesApi->list_rental_files: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **order_by** | **str**|  | [optional] [default to -created_at]
 **limit** | **int**|  | [optional] [default to 10]
 **offset** | **int**|  | [optional] [default to 0]
 **search** | **str**|  | [optional] 
 **product_id** | **str**|  | [optional] 
 **managers__in** | **str**|  | [optional] 
 **managers__nin** | **str**|  | [optional] 
 **managers__eq** | [**ManagersEq**](.md)|  | [optional] 
 **tags__in** | **str**|  | [optional] 
 **tags__nin** | **str**|  | [optional] 
 **tags__eq** | **str**|  | [optional] 
 **created_at__lte** | **datetime**|  | [optional] 
 **created_at__gte** | **datetime**|  | [optional] 
 **updated_at__lte** | **datetime**|  | [optional] 
 **updated_at__gte** | **datetime**|  | [optional] 
 **applicants_situation** | **str**|  | [optional] 
 **status** | **str**|  | [optional] 
 **decision** | **str**|  | [optional] 
 **archived** | **bool**|  | [optional] 
 **pre_application_validated** | **bool**|  | [optional] 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

[**PaginatedResponseListRentalFile**](PaginatedResponseListRentalFile.md)

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

# **lock_applicant_form**
> object lock_applicant_form(applicant_id, x_eaz_account_id=x_eaz_account_id)

Lock applicant form

This will change the form_submitted field for this applicant.

By triggering this, the applicant will not be able to change his form
and this will trigger the next step of the Applicant's lifecycle (1)

(1)
    - if no analysis has been asked the applicant will move to COLLECTED state
    - if analysis has been asked the applicant will be analyzed.

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
- `rental_file:write`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v2
from core.v2.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /v2
# See configuration.py for a list of all supported configuration parameters.
configuration = core.v2.Configuration(
    host = "/v2"
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
with core.v2.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = core.v2.RentalFilesApi(api_client)
    applicant_id = 'applicant_id_example' # str | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Lock applicant form
        api_response = api_instance.lock_applicant_form(applicant_id, x_eaz_account_id=x_eaz_account_id)
        print("The response of RentalFilesApi->lock_applicant_form:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RentalFilesApi->lock_applicant_form: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **applicant_id** | **str**|  | 
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
**202** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **partial_update_rental_file**
> RentalFile partial_update_rental_file(id, partial_update_rental_file, x_eaz_account_id=x_eaz_account_id)

Partial update rental file

Partially Update a Rental File by ID.

This endpoint allows the authenticated user to make partial updates to
a specific rental file using its unique identifier. Only the fields provided
in the request body will be updated.

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
- `rental_file:write`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v2
from core.v2.models.partial_update_rental_file import PartialUpdateRentalFile
from core.v2.models.rental_file import RentalFile
from core.v2.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /v2
# See configuration.py for a list of all supported configuration parameters.
configuration = core.v2.Configuration(
    host = "/v2"
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
with core.v2.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = core.v2.RentalFilesApi(api_client)
    id = 'id_example' # str | 
    partial_update_rental_file = core.v2.PartialUpdateRentalFile() # PartialUpdateRentalFile | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Partial update rental file
        api_response = api_instance.partial_update_rental_file(id, partial_update_rental_file, x_eaz_account_id=x_eaz_account_id)
        print("The response of RentalFilesApi->partial_update_rental_file:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RentalFilesApi->partial_update_rental_file: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **partial_update_rental_file** | [**PartialUpdateRentalFile**](PartialUpdateRentalFile.md)|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

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

# **reopen_all_forms**
> object reopen_all_forms(id, reopen_forms, x_eaz_account_id=x_eaz_account_id)

Reopen all forms

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
- `rental_file:write`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v2
from core.v2.models.reopen_forms import ReopenForms
from core.v2.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /v2
# See configuration.py for a list of all supported configuration parameters.
configuration = core.v2.Configuration(
    host = "/v2"
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
with core.v2.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = core.v2.RentalFilesApi(api_client)
    id = 'id_example' # str | 
    reopen_forms = core.v2.ReopenForms() # ReopenForms | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Reopen all forms
        api_response = api_instance.reopen_all_forms(id, reopen_forms, x_eaz_account_id=x_eaz_account_id)
        print("The response of RentalFilesApi->reopen_all_forms:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RentalFilesApi->reopen_all_forms: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **reopen_forms** | [**ReopenForms**](ReopenForms.md)|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

**object**

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reopen_applicant_form**
> object reopen_applicant_form(applicant_id, reopen_forms, x_eaz_account_id=x_eaz_account_id)

Reopen applicant form

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
- `rental_file:write`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v2
from core.v2.models.reopen_forms import ReopenForms
from core.v2.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /v2
# See configuration.py for a list of all supported configuration parameters.
configuration = core.v2.Configuration(
    host = "/v2"
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
with core.v2.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = core.v2.RentalFilesApi(api_client)
    applicant_id = 'applicant_id_example' # str | 
    reopen_forms = core.v2.ReopenForms() # ReopenForms | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Reopen applicant form
        api_response = api_instance.reopen_applicant_form(applicant_id, reopen_forms, x_eaz_account_id=x_eaz_account_id)
        print("The response of RentalFilesApi->reopen_applicant_form:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RentalFilesApi->reopen_applicant_form: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **applicant_id** | **str**|  | 
 **reopen_forms** | [**ReopenForms**](ReopenForms.md)|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

**object**

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_rental_file**
> RentalFile update_rental_file(id, update_rental_file, x_eaz_account_id=x_eaz_account_id)

Update rental file

Update a Rental File by ID.

This endpoint allows the authenticated user to make updates to
a specific rental file using its unique identifier. Only the fields provided
in the request body will be updated.

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
- `rental_file:write`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v2
from core.v2.models.rental_file import RentalFile
from core.v2.models.update_rental_file import UpdateRentalFile
from core.v2.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /v2
# See configuration.py for a list of all supported configuration parameters.
configuration = core.v2.Configuration(
    host = "/v2"
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
with core.v2.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = core.v2.RentalFilesApi(api_client)
    id = 'id_example' # str | 
    update_rental_file = core.v2.UpdateRentalFile() # UpdateRentalFile | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Update rental file
        api_response = api_instance.update_rental_file(id, update_rental_file, x_eaz_account_id=x_eaz_account_id)
        print("The response of RentalFilesApi->update_rental_file:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RentalFilesApi->update_rental_file: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **update_rental_file** | [**UpdateRentalFile**](UpdateRentalFile.md)|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

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

# **validate_pre_application**
> object validate_pre_application(id, reopen_forms, x_eaz_account_id=x_eaz_account_id)

Validate pre application

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
- `rental_file:write`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v2
from core.v2.models.reopen_forms import ReopenForms
from core.v2.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /v2
# See configuration.py for a list of all supported configuration parameters.
configuration = core.v2.Configuration(
    host = "/v2"
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
with core.v2.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = core.v2.RentalFilesApi(api_client)
    id = 'id_example' # str | 
    reopen_forms = core.v2.ReopenForms() # ReopenForms | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Validate pre application
        api_response = api_instance.validate_pre_application(id, reopen_forms, x_eaz_account_id=x_eaz_account_id)
        print("The response of RentalFilesApi->validate_pre_application:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RentalFilesApi->validate_pre_application: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **reopen_forms** | [**ReopenForms**](ReopenForms.md)|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

**object**

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

