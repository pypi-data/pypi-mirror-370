# iam.v1.TeamApi

All URIs are relative to */iam/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_organization_members**](TeamApi.md#add_organization_members) | **POST** /team/members/ | Add organization members
[**deactivate_member**](TeamApi.md#deactivate_member) | **POST** /team/members/{id}/deactivate/ | Deactivate member
[**delete_team_member**](TeamApi.md#delete_team_member) | **DELETE** /team/members/{id}/ | Delete team member
[**get_organization_member**](TeamApi.md#get_organization_member) | **GET** /team/members/{id}/ | Get organization member
[**list_organization_members**](TeamApi.md#list_organization_members) | **GET** /team/members/ | List organization members
[**lock_member**](TeamApi.md#lock_member) | **POST** /team/members/{id}/lock/ | Lock member
[**reactivate_member**](TeamApi.md#reactivate_member) | **POST** /team/members/{id}/reactivate/ | Reactivate member
[**sync_user_from_auth_service**](TeamApi.md#sync_user_from_auth_service) | **POST** /team/members/{id}/sync-from-auth/ | Sync user from auth service
[**unlock_member**](TeamApi.md#unlock_member) | **POST** /team/members/{id}/unlock/ | Unlock member
[**update_team_member**](TeamApi.md#update_team_member) | **PATCH** /team/members/{id}/ | Update team member


# **add_organization_members**
> User add_organization_members(create_user, x_eaz_account_id=x_eaz_account_id)

Add organization members

Add/Invite a member in the organization.

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
from iam.v1.models.create_user import CreateUser
from iam.v1.models.user import User
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
    api_instance = iam.v1.TeamApi(api_client)
    create_user = iam.v1.CreateUser() # CreateUser | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Add organization members
        api_response = api_instance.add_organization_members(create_user, x_eaz_account_id=x_eaz_account_id)
        print("The response of TeamApi->add_organization_members:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamApi->add_organization_members: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_user** | [**CreateUser**](CreateUser.md)|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

[**User**](User.md)

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

# **deactivate_member**
> User deactivate_member(id, x_eaz_account_id=x_eaz_account_id)

Deactivate member

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
from iam.v1.models.user import User
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
    api_instance = iam.v1.TeamApi(api_client)
    id = 'id_example' # str | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Deactivate member
        api_response = api_instance.deactivate_member(id, x_eaz_account_id=x_eaz_account_id)
        print("The response of TeamApi->deactivate_member:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamApi->deactivate_member: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

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
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_team_member**
> delete_team_member(id, x_eaz_account_id=x_eaz_account_id)

Delete team member

Delete member from the organization.

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
    api_instance = iam.v1.TeamApi(api_client)
    id = 'id_example' # str | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Delete team member
        api_instance.delete_team_member(id, x_eaz_account_id=x_eaz_account_id)
    except Exception as e:
        print("Exception when calling TeamApi->delete_team_member: %s\n" % e)
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

# **get_organization_member**
> User get_organization_member(id, x_eaz_account_id=x_eaz_account_id)

Get organization member

Get member from the organization.

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
from iam.v1.models.user import User
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
    api_instance = iam.v1.TeamApi(api_client)
    id = 'id_example' # str | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Get organization member
        api_response = api_instance.get_organization_member(id, x_eaz_account_id=x_eaz_account_id)
        print("The response of TeamApi->get_organization_member:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamApi->get_organization_member: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

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
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_organization_members**
> List[ListUser] list_organization_members(x_eaz_account_id=x_eaz_account_id)

List organization members

List all members from the organization.

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
from iam.v1.models.list_user import ListUser
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
    api_instance = iam.v1.TeamApi(api_client)
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # List organization members
        api_response = api_instance.list_organization_members(x_eaz_account_id=x_eaz_account_id)
        print("The response of TeamApi->list_organization_members:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamApi->list_organization_members: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

[**List[ListUser]**](ListUser.md)

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

# **lock_member**
> User lock_member(id, x_eaz_account_id=x_eaz_account_id)

Lock member

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
from iam.v1.models.user import User
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
    api_instance = iam.v1.TeamApi(api_client)
    id = 'id_example' # str | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Lock member
        api_response = api_instance.lock_member(id, x_eaz_account_id=x_eaz_account_id)
        print("The response of TeamApi->lock_member:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamApi->lock_member: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

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
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reactivate_member**
> User reactivate_member(id, x_eaz_account_id=x_eaz_account_id)

Reactivate member

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
from iam.v1.models.user import User
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
    api_instance = iam.v1.TeamApi(api_client)
    id = 'id_example' # str | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Reactivate member
        api_response = api_instance.reactivate_member(id, x_eaz_account_id=x_eaz_account_id)
        print("The response of TeamApi->reactivate_member:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamApi->reactivate_member: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

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
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **sync_user_from_auth_service**
> object sync_user_from_auth_service(id, x_eaz_account_id=x_eaz_account_id)

Sync user from auth service

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
    api_instance = iam.v1.TeamApi(api_client)
    id = 'id_example' # str | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Sync user from auth service
        api_response = api_instance.sync_user_from_auth_service(id, x_eaz_account_id=x_eaz_account_id)
        print("The response of TeamApi->sync_user_from_auth_service:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamApi->sync_user_from_auth_service: %s\n" % e)
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

# **unlock_member**
> User unlock_member(id, x_eaz_account_id=x_eaz_account_id)

Unlock member

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
from iam.v1.models.user import User
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
    api_instance = iam.v1.TeamApi(api_client)
    id = 'id_example' # str | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Unlock member
        api_response = api_instance.unlock_member(id, x_eaz_account_id=x_eaz_account_id)
        print("The response of TeamApi->unlock_member:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamApi->unlock_member: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

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
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_team_member**
> User update_team_member(id, partial_update_user, x_eaz_account_id=x_eaz_account_id)

Update team member

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
from iam.v1.models.partial_update_user import PartialUpdateUser
from iam.v1.models.user import User
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
    api_instance = iam.v1.TeamApi(api_client)
    id = 'id_example' # str | 
    partial_update_user = iam.v1.PartialUpdateUser() # PartialUpdateUser | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Update team member
        api_response = api_instance.update_team_member(id, partial_update_user, x_eaz_account_id=x_eaz_account_id)
        print("The response of TeamApi->update_team_member:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamApi->update_team_member: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **partial_update_user** | [**PartialUpdateUser**](PartialUpdateUser.md)|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

[**User**](User.md)

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

