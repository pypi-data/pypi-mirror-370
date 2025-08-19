# core.v1.SupportingDocumentsApi

All URIs are relative to */v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_document**](SupportingDocumentsApi.md#create_document) | **POST** /supporting-documents | Create document
[**get_document**](SupportingDocumentsApi.md#get_document) | **GET** /supporting-documents/{id} | Get document
[**list_documents**](SupportingDocumentsApi.md#list_documents) | **GET** /supporting-documents | List documents


# **create_document**
> SupportingDocument create_document(files, applicant, document_type)

Create document

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
from core.v1.models.supporting_document import SupportingDocument
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
    api_instance = core.v1.SupportingDocumentsApi(api_client)
    files = None # List[bytearray] | 
    applicant = 'applicant_example' # str | 
    document_type = 'document_type_example' # str | 

    try:
        # Create document
        api_response = api_instance.create_document(files, applicant, document_type)
        print("The response of SupportingDocumentsApi->create_document:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SupportingDocumentsApi->create_document: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **files** | **List[bytearray]**|  | 
 **applicant** | **str**|  | 
 **document_type** | **str**|  | 

### Return type

[**SupportingDocument**](SupportingDocument.md)

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

# **get_document**
> SupportingDocument get_document(id)

Get document

## 🔒 Authentication

This endpoint require a valid OAuth2 Bearer
### Scopes : 
User must provide one of the following scopes:
- `admin`
- `staff`
- `user`
- `org:admin`
- `org:staff`
- `rental_file:read`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v1
from core.v1.models.supporting_document import SupportingDocument
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
    api_instance = core.v1.SupportingDocumentsApi(api_client)
    id = 'id_example' # str | 

    try:
        # Get document
        api_response = api_instance.get_document(id)
        print("The response of SupportingDocumentsApi->get_document:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SupportingDocumentsApi->get_document: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

[**SupportingDocument**](SupportingDocument.md)

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

# **list_documents**
> PaginatedResponseSupportingDocumentList list_documents(order_by=order_by, limit=limit, offset=offset, applicant=applicant, applicant_file=applicant_file, applicant_reference=applicant_reference, applicant_file_reference=applicant_file_reference, document_type=document_type, internal_model=internal_model, status=status)

List documents

## 🔒 Authentication

This endpoint require a valid OAuth2 Bearer
### Scopes : 
User must provide one of the following scopes:
- `admin`
- `staff`
- `user`
- `org:admin`
- `org:staff`
- `rental_file:read`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v1
from core.v1.models.paginated_response_supporting_document_list import PaginatedResponseSupportingDocumentList
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
    api_instance = core.v1.SupportingDocumentsApi(api_client)
    order_by = -created_at # str |  (optional) (default to -created_at)
    limit = 10 # int |  (optional) (default to 10)
    offset = 0 # int |  (optional) (default to 0)
    applicant = 'applicant_example' # str |  (optional)
    applicant_file = 'applicant_file_example' # str |  (optional)
    applicant_reference = 'applicant_reference_example' # str |  (optional)
    applicant_file_reference = 'applicant_file_reference_example' # str |  (optional)
    document_type = 'document_type_example' # str |  (optional)
    internal_model = 'internal_model_example' # str |  (optional)
    status = 'status_example' # str |  (optional)

    try:
        # List documents
        api_response = api_instance.list_documents(order_by=order_by, limit=limit, offset=offset, applicant=applicant, applicant_file=applicant_file, applicant_reference=applicant_reference, applicant_file_reference=applicant_file_reference, document_type=document_type, internal_model=internal_model, status=status)
        print("The response of SupportingDocumentsApi->list_documents:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SupportingDocumentsApi->list_documents: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **order_by** | **str**|  | [optional] [default to -created_at]
 **limit** | **int**|  | [optional] [default to 10]
 **offset** | **int**|  | [optional] [default to 0]
 **applicant** | **str**|  | [optional] 
 **applicant_file** | **str**|  | [optional] 
 **applicant_reference** | **str**|  | [optional] 
 **applicant_file_reference** | **str**|  | [optional] 
 **document_type** | **str**|  | [optional] 
 **internal_model** | **str**|  | [optional] 
 **status** | **str**|  | [optional] 

### Return type

[**PaginatedResponseSupportingDocumentList**](PaginatedResponseSupportingDocumentList.md)

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

