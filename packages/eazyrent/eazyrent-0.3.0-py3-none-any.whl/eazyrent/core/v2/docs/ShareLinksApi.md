# core.v2.ShareLinksApi

All URIs are relative to */v2*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_share_link**](ShareLinksApi.md#create_share_link) | **POST** /share-links/ | Create share link
[**delete_share_link**](ShareLinksApi.md#delete_share_link) | **DELETE** /share-links/{secret}/ | Delete share link
[**get_rental_file_by_secret**](ShareLinksApi.md#get_rental_file_by_secret) | **GET** /share-links/{secret}/rental-file/ | Get rental file by secret
[**get_share_links**](ShareLinksApi.md#get_share_links) | **GET** /share-links/{rental_file_id}/ | Get share links


# **create_share_link**
> object create_share_link(rental_file_id, expiry_date=expiry_date, x_eaz_account_id=x_eaz_account_id)

Create share link

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
    api_instance = core.v2.ShareLinksApi(api_client)
    rental_file_id = 'rental_file_id_example' # str | 
    expiry_date = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Create share link
        api_response = api_instance.create_share_link(rental_file_id, expiry_date=expiry_date, x_eaz_account_id=x_eaz_account_id)
        print("The response of ShareLinksApi->create_share_link:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ShareLinksApi->create_share_link: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **rental_file_id** | **str**|  | 
 **expiry_date** | **datetime**|  | [optional] 
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
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_share_link**
> delete_share_link(secret, x_eaz_account_id=x_eaz_account_id)

Delete share link

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
    api_instance = core.v2.ShareLinksApi(api_client)
    secret = 'secret_example' # str | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Delete share link
        api_instance.delete_share_link(secret, x_eaz_account_id=x_eaz_account_id)
    except Exception as e:
        print("Exception when calling ShareLinksApi->delete_share_link: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **secret** | **str**|  | 
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

# **get_rental_file_by_secret**
> RentalFile get_rental_file_by_secret(secret)

Get rental file by secret

### Example


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


# Enter a context with an instance of the API client
with core.v2.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = core.v2.ShareLinksApi(api_client)
    secret = 'secret_example' # str | 

    try:
        # Get rental file by secret
        api_response = api_instance.get_rental_file_by_secret(secret)
        print("The response of ShareLinksApi->get_rental_file_by_secret:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ShareLinksApi->get_rental_file_by_secret: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **secret** | **str**|  | 

### Return type

[**RentalFile**](RentalFile.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_share_links**
> object get_share_links(rental_file_id, x_eaz_account_id=x_eaz_account_id)

Get share links

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
    api_instance = core.v2.ShareLinksApi(api_client)
    rental_file_id = 'rental_file_id_example' # str | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Get share links
        api_response = api_instance.get_share_links(rental_file_id, x_eaz_account_id=x_eaz_account_id)
        print("The response of ShareLinksApi->get_share_links:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ShareLinksApi->get_share_links: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **rental_file_id** | **str**|  | 
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

