# core.v2.TagsApi

All URIs are relative to */v2*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_account_tags**](TagsApi.md#list_account_tags) | **GET** /tags/ | List account tags


# **list_account_tags**
> List[Tag] list_account_tags(x_eaz_account_id=x_eaz_account_id)

List account tags

Retrieve a list of tags associated with the authenticated user's account.

This endpoint allows the authenticated user to obtain a list of tags
that are associated with their account. Tags may represent various
attributes or categories relevant to the account's information
and usage.

## Authentication:
- Requires a valid OAuth access token with any of the following scopes:
  - Internal Scopes:
    - `admin`
    - `staff`
    - `user`
  - Public Scopes:
    - `org:admin`
    - `org:staff`
    - `org:user`

## Response:
- **200 OK**: Returns a list of tags in JSON format.
  - Each tag contains relevant information for the account.
- **403 Forbidden**: If the user does not have the required scope.
- **401 Unauthorized**: If the request does not include valid authentication.

## Response Model:
- **List[Tag]**: Each tag contains fields such as `name`, and other metadata.

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v2
from core.v2.models.tag import Tag
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
    api_instance = core.v2.TagsApi(api_client)
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # List account tags
        api_response = api_instance.list_account_tags(x_eaz_account_id=x_eaz_account_id)
        print("The response of TagsApi->list_account_tags:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TagsApi->list_account_tags: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

[**List[Tag]**](Tag.md)

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

