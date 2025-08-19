# iam.v1.UserGrantsApi

All URIs are relative to */iam/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**retrieve_my_authorizations**](UserGrantsApi.md#retrieve_my_authorizations) | **GET** /user-grants/me/authorizations/ | Retrieve my authorizations
[**retrieve_user_authorizations**](UserGrantsApi.md#retrieve_user_authorizations) | **GET** /user-grants/{user_id}/authorizations/ | Retrieve user authorizations
[**update_user_authorizations**](UserGrantsApi.md#update_user_authorizations) | **PUT** /user-grants/{user_id}/authorizations/ | Update user authorizations


# **retrieve_my_authorizations**
> object retrieve_my_authorizations()

Retrieve my authorizations

Retrieve Current User Authorizations.

This endpoint retrieves all authorization grants for the currently authenticated
user using the Zitadel client. It queries the user's organization for available
grants and returns them in a list.

## Response:
- **200 OK**: Returns a list of authorization grants for the current user.
- **401 Unauthorized**: If the user is not authenticated.
- **403 Forbidden**: If the user lacks necessary permissions.

## 🔒 Authentication

This endpoint require a valid OAuth2 Bearer

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import iam.v1
from iam.v1.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /iam/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = iam.v1.Configuration(
    host = "/iam/v1"
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
with iam.v1.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = iam.v1.UserGrantsApi(api_client)

    try:
        # Retrieve my authorizations
        api_response = api_instance.retrieve_my_authorizations()
        print("The response of UserGrantsApi->retrieve_my_authorizations:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UserGrantsApi->retrieve_my_authorizations: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **retrieve_user_authorizations**
> object retrieve_user_authorizations(user_id, x_eaz_account_id=x_eaz_account_id)

Retrieve user authorizations

Retrieve User Authorizations.

This endpoint fetches the groups or permissions for a specific user.
It searches for the user within the organization of the authenticated client
and returns the user's roles or permissions.

## Path Parameters:
- **user_id** (required): The unique identifier of the user whose
authorizations are to be retrieved.

## Response:
- **200 OK**: Returns a list of groups or permissions for the specified user.
- **404 Not Found**: If the user is not found within the authenticated
organization.

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
- `organization:read`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import iam.v1
from iam.v1.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /iam/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = iam.v1.Configuration(
    host = "/iam/v1"
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
with iam.v1.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = iam.v1.UserGrantsApi(api_client)
    user_id = 'user_id_example' # str | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Retrieve user authorizations
        api_response = api_instance.retrieve_user_authorizations(user_id, x_eaz_account_id=x_eaz_account_id)
        print("The response of UserGrantsApi->retrieve_user_authorizations:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UserGrantsApi->retrieve_user_authorizations: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**|  | 
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

# **update_user_authorizations**
> object update_user_authorizations(user_id, update_user_grants, x_eaz_account_id=x_eaz_account_id)

Update user authorizations

Update User Authorizations.

This endpoint updates a user's authorizations by assigning a new role.
It fetches the user from the authenticated client's organization and updates
their project roles accordingly.

## Path Parameters:
- **user_id** (required): The unique identifier of the user whose
authorizations are updated.

## Request Body:
- **role** (required): A role to assign to the user. Must be one of:
- `org:admin`
- `org:staff`
- `org:user`

## Response:
- **200 OK**: Returns the updated list of user roles.
- **404 Not Found**: If the user is not found in the authenticated organization.

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
- `organization:write`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import iam.v1
from iam.v1.models.update_user_grants import UpdateUserGrants
from iam.v1.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /iam/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = iam.v1.Configuration(
    host = "/iam/v1"
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
with iam.v1.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = iam.v1.UserGrantsApi(api_client)
    user_id = 'user_id_example' # str | 
    update_user_grants = iam.v1.UpdateUserGrants() # UpdateUserGrants | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Update user authorizations
        api_response = api_instance.update_user_authorizations(user_id, update_user_grants, x_eaz_account_id=x_eaz_account_id)
        print("The response of UserGrantsApi->update_user_authorizations:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UserGrantsApi->update_user_authorizations: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**|  | 
 **update_user_grants** | [**UpdateUserGrants**](UpdateUserGrants.md)|  | 
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

