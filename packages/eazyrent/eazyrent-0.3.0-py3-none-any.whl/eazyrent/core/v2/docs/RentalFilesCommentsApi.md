# core.v2.RentalFilesCommentsApi

All URIs are relative to */v2*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_comment**](RentalFilesCommentsApi.md#add_comment) | **POST** /rental-files/{id}/comments | Add comment
[**delete_comment**](RentalFilesCommentsApi.md#delete_comment) | **DELETE** /rental-files/{id}/comments/{comment_id} | Delete comment
[**get_comments**](RentalFilesCommentsApi.md#get_comments) | **GET** /rental-files/{id}/comments | Get comments
[**update_comment**](RentalFilesCommentsApi.md#update_comment) | **PATCH** /rental-files/{id}/comments/{comment_id} | Update comment


# **add_comment**
> RentalFileComment add_comment(id, rental_file_comment_in, x_eaz_account_id=x_eaz_account_id)

Add comment

Add a comment to a Rental File.

This endpoint allows the authenticated user to add a comment to a
specific rental file. Comments can provide additional information,
feedback, or questions related to the rental file.

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
from core.v2.models.rental_file_comment import RentalFileComment
from core.v2.models.rental_file_comment_in import RentalFileCommentIn
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
    api_instance = core.v2.RentalFilesCommentsApi(api_client)
    id = 'id_example' # str | 
    rental_file_comment_in = core.v2.RentalFileCommentIn() # RentalFileCommentIn | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Add comment
        api_response = api_instance.add_comment(id, rental_file_comment_in, x_eaz_account_id=x_eaz_account_id)
        print("The response of RentalFilesCommentsApi->add_comment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RentalFilesCommentsApi->add_comment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **rental_file_comment_in** | [**RentalFileCommentIn**](RentalFileCommentIn.md)|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

[**RentalFileComment**](RentalFileComment.md)

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

# **delete_comment**
> delete_comment(id, comment_id, x_eaz_account_id=x_eaz_account_id)

Delete comment

Delete a comment from a Rental File.

This endpoint allows the authenticated user to delete a specific
comment from a rental file. This can be useful for removing outdated
or irrelevant comments.

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
    api_instance = core.v2.RentalFilesCommentsApi(api_client)
    id = 'id_example' # str | 
    comment_id = 'comment_id_example' # str | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Delete comment
        api_instance.delete_comment(id, comment_id, x_eaz_account_id=x_eaz_account_id)
    except Exception as e:
        print("Exception when calling RentalFilesCommentsApi->delete_comment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **comment_id** | **str**|  | 
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

# **get_comments**
> object get_comments(id, x_eaz_account_id=x_eaz_account_id)

Get comments

Retrieve all comments on a Rental File.

This endpoint allows the authenticated user to retrieve all comments
associated with a specific rental file. The comments provide insights
and feedback related to the rental file from different users.

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
    api_instance = core.v2.RentalFilesCommentsApi(api_client)
    id = 'id_example' # str | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Get comments
        api_response = api_instance.get_comments(id, x_eaz_account_id=x_eaz_account_id)
        print("The response of RentalFilesCommentsApi->get_comments:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RentalFilesCommentsApi->get_comments: %s\n" % e)
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

# **update_comment**
> RentalFileComment update_comment(id, comment_id, rental_file_comment_in, x_eaz_account_id=x_eaz_account_id)

Update comment

Update a comment on a Rental File.

This endpoint allows the authenticated user to update an existing
comment on a specific rental file. This can be useful for
correcting or adding to the information provided in the original comment.

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
from core.v2.models.rental_file_comment import RentalFileComment
from core.v2.models.rental_file_comment_in import RentalFileCommentIn
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
    api_instance = core.v2.RentalFilesCommentsApi(api_client)
    id = 'id_example' # str | 
    comment_id = 'comment_id_example' # str | 
    rental_file_comment_in = core.v2.RentalFileCommentIn() # RentalFileCommentIn | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Update comment
        api_response = api_instance.update_comment(id, comment_id, rental_file_comment_in, x_eaz_account_id=x_eaz_account_id)
        print("The response of RentalFilesCommentsApi->update_comment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RentalFilesCommentsApi->update_comment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **comment_id** | **str**|  | 
 **rental_file_comment_in** | [**RentalFileCommentIn**](RentalFileCommentIn.md)|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

[**RentalFileComment**](RentalFileComment.md)

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

