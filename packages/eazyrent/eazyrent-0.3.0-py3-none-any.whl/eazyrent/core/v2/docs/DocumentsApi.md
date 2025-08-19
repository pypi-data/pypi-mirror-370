# core.v2.DocumentsApi

All URIs are relative to */v2*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_document**](DocumentsApi.md#create_document) | **POST** /documents/ | Create document
[**deleted_document**](DocumentsApi.md#deleted_document) | **DELETE** /documents/{id}/ | Deleted document
[**download_document**](DocumentsApi.md#download_document) | **GET** /documents/{id}/download/ | Download document
[**reject_document**](DocumentsApi.md#reject_document) | **POST** /documents/{id}/reject/ | Reject document


# **create_document**
> object create_document(file, applicant, document_type, x_eaz_account_id=x_eaz_account_id)

Create document

Upload a Document for Analysis.

This endpoint allows the authenticated user to upload a document for analysis
associated with a specific applicant. Supported document formats include PDF and
image formats (JPEG, PNG), and the uploaded file is stored for processing.

**Apple's HEIC format is not supported**

## Authentication:
- Requires a valid OAuth access token with the following scopes:
  - `document:write`
  - Or one of the internal scopes: `org:staff`, `org:admin`, `admin`
  - Public scopes may also be included.

## Parameters:
- **file** (required, form): The document file to upload. Supported formats:
  - `application/pdf`
  - `image/jpeg`
  - `image/png`
- **applicant** (required, form): The unique identifier (UUID) of the applicant
  to whom the document is associated.
- **document_type** (required, form): The unique identifier (UUID) representing
  the type of document being uploaded.

## Response:
- **201 Created**: Returns the details of the uploaded document, including
  its storage reference and metadata.
- **404 Not Found**: If the applicant or the document type associated with the
  provided ID cannot be found.
- **400 Bad Request**: If the uploaded file is of an unsupported format or
  if any of the required parameters are missing.
- **413 Payload Too Large**: If the uploaded file exceeds the maximum size limit
  of 50 MB.
- **403 Forbidden**: If the user does not have the necessary permissions
  to upload the document.

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
- `document:write`

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
    api_instance = core.v2.DocumentsApi(api_client)
    file = None # bytearray | 
    applicant = 'applicant_example' # str | 
    document_type = 'document_type_example' # str | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Create document
        api_response = api_instance.create_document(file, applicant, document_type, x_eaz_account_id=x_eaz_account_id)
        print("The response of DocumentsApi->create_document:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->create_document: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file** | **bytearray**|  | 
 **applicant** | **str**|  | 
 **document_type** | **str**|  | 
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

# **deleted_document**
> deleted_document(id, x_eaz_account_id=x_eaz_account_id)

Deleted document

Delete a Document.

This endpoint allows the authenticated user to delete a specific document
associated with their organization. The document ID must be provided to identify
which document to delete.

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
- `document:write`

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
    api_instance = core.v2.DocumentsApi(api_client)
    id = 'id_example' # str | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Deleted document
        api_instance.deleted_document(id, x_eaz_account_id=x_eaz_account_id)
    except Exception as e:
        print("Exception when calling DocumentsApi->deleted_document: %s\n" % e)
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

# **download_document**
> download_document(id, x_eaz_account_id=x_eaz_account_id)

Download document

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
    api_instance = core.v2.DocumentsApi(api_client)
    id = 'id_example' # str | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Download document
        api_instance.download_document(id, x_eaz_account_id=x_eaz_account_id)
    except Exception as e:
        print("Exception when calling DocumentsApi->download_document: %s\n" % e)
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
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reject_document**
> object reject_document(id, reject_reason, x_eaz_account_id=x_eaz_account_id)

Reject document

Reject a Document.

This endpoint allows the authenticated user to reject a specific document
associated with their organization.

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
- `document:write`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v2
from core.v2.models.reject_reason import RejectReason
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
    api_instance = core.v2.DocumentsApi(api_client)
    id = 'id_example' # str | 
    reject_reason = core.v2.RejectReason() # RejectReason | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Reject document
        api_response = api_instance.reject_document(id, reject_reason, x_eaz_account_id=x_eaz_account_id)
        print("The response of DocumentsApi->reject_document:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->reject_document: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **reject_reason** | [**RejectReason**](RejectReason.md)|  | 
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

