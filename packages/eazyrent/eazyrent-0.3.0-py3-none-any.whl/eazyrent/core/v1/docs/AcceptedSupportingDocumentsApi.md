# core.v1.AcceptedSupportingDocumentsApi

All URIs are relative to */v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_accepted_document**](AcceptedSupportingDocumentsApi.md#get_accepted_document) | **GET** /accepted-supporting-documents/{id} | Get accepted document
[**list_accepted_documents**](AcceptedSupportingDocumentsApi.md#list_accepted_documents) | **GET** /accepted-supporting-documents | List accepted documents


# **get_accepted_document**
> AcceptedSupportingDocument get_accepted_document(id)

Get accepted document

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
- `organization:read`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v1
from core.v1.models.accepted_supporting_document import AcceptedSupportingDocument
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
    api_instance = core.v1.AcceptedSupportingDocumentsApi(api_client)
    id = 'id_example' # str | 

    try:
        # Get accepted document
        api_response = api_instance.get_accepted_document(id)
        print("The response of AcceptedSupportingDocumentsApi->get_accepted_document:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AcceptedSupportingDocumentsApi->get_accepted_document: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

[**AcceptedSupportingDocument**](AcceptedSupportingDocument.md)

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

# **list_accepted_documents**
> PaginatedResponseAcceptedSupportingDocument list_accepted_documents(order_by=order_by, limit=limit, offset=offset, analyze_as=analyze_as, analyzed=analyzed, category=category, search=search)

List accepted documents

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
- `organization:read`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v1
from core.v1.models.paginated_response_accepted_supporting_document import PaginatedResponseAcceptedSupportingDocument
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
    api_instance = core.v1.AcceptedSupportingDocumentsApi(api_client)
    order_by = name # str |  (optional) (default to name)
    limit = 10 # int |  (optional) (default to 10)
    offset = 0 # int |  (optional) (default to 0)
    analyze_as = 'analyze_as_example' # str |  (optional)
    analyzed = True # bool |  (optional)
    category = 'category_example' # str |  (optional)
    search = 'search_example' # str |  (optional)

    try:
        # List accepted documents
        api_response = api_instance.list_accepted_documents(order_by=order_by, limit=limit, offset=offset, analyze_as=analyze_as, analyzed=analyzed, category=category, search=search)
        print("The response of AcceptedSupportingDocumentsApi->list_accepted_documents:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AcceptedSupportingDocumentsApi->list_accepted_documents: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **order_by** | **str**|  | [optional] [default to name]
 **limit** | **int**|  | [optional] [default to 10]
 **offset** | **int**|  | [optional] [default to 0]
 **analyze_as** | **str**|  | [optional] 
 **analyzed** | **bool**|  | [optional] 
 **category** | **str**|  | [optional] 
 **search** | **str**|  | [optional] 

### Return type

[**PaginatedResponseAcceptedSupportingDocument**](PaginatedResponseAcceptedSupportingDocument.md)

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

