# iam.v1.PublicApi

All URIs are relative to */iam/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**register**](PublicApi.md#register) | **POST** /register/ | Register


# **register**
> RegisterSerializer register(register_serializer)

Register

Register a new account.

### Example


```python
import iam.v1
from iam.v1.models.register_serializer import RegisterSerializer
from iam.v1.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /iam/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = iam.v1.Configuration(
    host = "/iam/v1"
)


# Enter a context with an instance of the API client
with iam.v1.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = iam.v1.PublicApi(api_client)
    register_serializer = iam.v1.RegisterSerializer() # RegisterSerializer | 

    try:
        # Register
        api_response = api_instance.register(register_serializer)
        print("The response of PublicApi->register:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->register: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **register_serializer** | [**RegisterSerializer**](RegisterSerializer.md)|  | 

### Return type

[**RegisterSerializer**](RegisterSerializer.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

