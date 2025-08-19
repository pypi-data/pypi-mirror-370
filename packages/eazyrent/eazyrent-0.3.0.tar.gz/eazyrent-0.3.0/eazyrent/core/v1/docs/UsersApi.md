# core.v1.UsersApi

All URIs are relative to */v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_current_user**](UsersApi.md#get_current_user) | **GET** /users/me | Get current user


# **get_current_user**
> User get_current_user()

Get current user

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import core.v1
from core.v1.models.user import User
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
    api_instance = core.v1.UsersApi(api_client)

    try:
        # Get current user
        api_response = api_instance.get_current_user()
        print("The response of UsersApi->get_current_user:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsersApi->get_current_user: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**User**](User.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

