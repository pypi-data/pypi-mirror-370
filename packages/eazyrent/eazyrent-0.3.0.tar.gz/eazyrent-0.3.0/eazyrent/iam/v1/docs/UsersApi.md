# iam.v1.UsersApi

All URIs are relative to */iam/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**change_my_password**](UsersApi.md#change_my_password) | **POST** /users/me/password/ | Change my password
[**create_profile_avatar**](UsersApi.md#create_profile_avatar) | **POST** /users/me/avatar/ | Create profile avatar
[**delete_my_user**](UsersApi.md#delete_my_user) | **DELETE** /users/me/ | Delete my user
[**delete_profile_avatar**](UsersApi.md#delete_profile_avatar) | **DELETE** /users/me/avatar/ | Delete profile avatar
[**get_my_config**](UsersApi.md#get_my_config) | **GET** /users/me/config/ | Get my config
[**get_my_user**](UsersApi.md#get_my_user) | **GET** /users/me/ | Get my user
[**get_user_notification_preferences**](UsersApi.md#get_user_notification_preferences) | **GET** /users/me/notification-preferences/ | Get user notification preferences
[**partial_update_my_user**](UsersApi.md#partial_update_my_user) | **PATCH** /users/me/ | Partial update my user
[**sync_my_user_from_auth_service**](UsersApi.md#sync_my_user_from_auth_service) | **POST** /users/me/sync-from-auth/ | Sync my user from auth service
[**update_my_config**](UsersApi.md#update_my_config) | **PUT** /users/me/config/ | Update my config
[**update_user_notification_preferences**](UsersApi.md#update_user_notification_preferences) | **PUT** /users/me/notification-preferences/ | Update user notification preferences


# **change_my_password**
> object change_my_password(change_password)

Change my password

Change Current User Password.

This endpoint allows an authenticated human user to change their password.
The user must provide their current password along with the new password.

## Request Body:
- **passwords** (required): An object containing:
- `current_password` (str): The user's current password.
- `new_password` (str): The new password to be set.

## Response:
- **202 Accepted**: Password change request has been accepted.
- **404 Not Found**: If the user is not found.
- **400 Bad Request**: If the provided password is incorrect or does not meet
security requirements.

## Notes:

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import iam.v1
from iam.v1.models.change_password import ChangePassword
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
    api_instance = iam.v1.UsersApi(api_client)
    change_password = iam.v1.ChangePassword() # ChangePassword | 

    try:
        # Change my password
        api_response = api_instance.change_my_password(change_password)
        print("The response of UsersApi->change_my_password:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsersApi->change_my_password: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **change_password** | [**ChangePassword**](ChangePassword.md)|  | 

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

# **create_profile_avatar**
> User create_profile_avatar(file)

Create profile avatar

## 🔒 Authentication

This endpoint require a valid OAuth2 Bearer

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
    api_instance = iam.v1.UsersApi(api_client)
    file = None # bytearray | 

    try:
        # Create profile avatar
        api_response = api_instance.create_profile_avatar(file)
        print("The response of UsersApi->create_profile_avatar:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsersApi->create_profile_avatar: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file** | **bytearray**|  | 

### Return type

[**User**](User.md)

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

# **delete_my_user**
> delete_my_user()

Delete my user

Delete Current User.

This endpoint allows an authenticated human user to delete their own account.
Once deleted, the account cannot be recovered.

## Response:
- **410 Gone**: The user account has been successfully deleted.
- **404 Not Found**: If the user does not exist.

## Notes:
- This action is irreversible.
- Only applicable to human users.

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
    api_instance = iam.v1.UsersApi(api_client)

    try:
        # Delete my user
        api_instance.delete_my_user()
    except Exception as e:
        print("Exception when calling UsersApi->delete_my_user: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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
**410** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_profile_avatar**
> object delete_profile_avatar()

Delete profile avatar

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
    api_instance = iam.v1.UsersApi(api_client)

    try:
        # Delete profile avatar
        api_response = api_instance.delete_profile_avatar()
        print("The response of UsersApi->delete_profile_avatar:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsersApi->delete_profile_avatar: %s\n" % e)
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
**202** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_my_config**
> UserConfig get_my_config()

Get my config

Retrieve Current User Configuration.

This endpoint returns the configuration settings of the currently
authenticated human user.

## Response:
- **200 OK**: Returns the user's configuration settings.
- **404 Not Found**: If the user is not found or is not a human user.

## Notes:
- The configuration is applicable only for human users.

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import iam.v1
from iam.v1.models.user_config import UserConfig
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
    api_instance = iam.v1.UsersApi(api_client)

    try:
        # Get my config
        api_response = api_instance.get_my_config()
        print("The response of UsersApi->get_my_config:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsersApi->get_my_config: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**UserConfig**](UserConfig.md)

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

# **get_my_user**
> ResponseGetMyUser get_my_user()

Get my user

Retrieve the Current User.

This endpoint returns the details of the currently authenticated user.
It supports both human and machine users by returning either a User or a
ServiceAccount model representation.

## Response:
- **200 OK**: Returns the current user's details.
- **401 Unauthorized**: If the user is not authenticated.

## 🔒 Authentication

This endpoint require a valid OAuth2 Bearer

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import iam.v1
from iam.v1.models.response_get_my_user import ResponseGetMyUser
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
    api_instance = iam.v1.UsersApi(api_client)

    try:
        # Get my user
        api_response = api_instance.get_my_user()
        print("The response of UsersApi->get_my_user:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsersApi->get_my_user: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**ResponseGetMyUser**](ResponseGetMyUser.md)

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

# **get_user_notification_preferences**
> NotificationConfig get_user_notification_preferences()

Get user notification preferences

Get Notification Preferences.

This endpoint retrieves the notification preferences of the authenticated user.

## Response:
- **200 OK**: Returns the user's notification preferences.
- **404 Not Found**: If the user does not exist.

## Notes:
- Only applicable to human users.

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import iam.v1
from iam.v1.models.notification_config import NotificationConfig
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
    api_instance = iam.v1.UsersApi(api_client)

    try:
        # Get user notification preferences
        api_response = api_instance.get_user_notification_preferences()
        print("The response of UsersApi->get_user_notification_preferences:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsersApi->get_user_notification_preferences: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**NotificationConfig**](NotificationConfig.md)

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

# **partial_update_my_user**
> User partial_update_my_user(partial_update_user)

Partial update my user

Partially Update the Current User.

This endpoint allows an authenticated user to update their profile with
partial update data.

## Request Body:
- **user_update** (required): An object containing the fields to update.
Only provided fields will be updated.

## Response:
- **200 OK**: Returns the updated user details.
- **404 Not Found**: If the current user is not found.

## Notes:
- Only the fields present in the request body are updated.

## 🔒 Authentication

This endpoint require a valid OAuth2 Bearer

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
    api_instance = iam.v1.UsersApi(api_client)
    partial_update_user = iam.v1.PartialUpdateUser() # PartialUpdateUser | 

    try:
        # Partial update my user
        api_response = api_instance.partial_update_my_user(partial_update_user)
        print("The response of UsersApi->partial_update_my_user:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsersApi->partial_update_my_user: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **partial_update_user** | [**PartialUpdateUser**](PartialUpdateUser.md)|  | 

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

# **sync_my_user_from_auth_service**
> object sync_my_user_from_auth_service()

Sync my user from auth service

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
    api_instance = iam.v1.UsersApi(api_client)

    try:
        # Sync my user from auth service
        api_response = api_instance.sync_my_user_from_auth_service()
        print("The response of UsersApi->sync_my_user_from_auth_service:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsersApi->sync_my_user_from_auth_service: %s\n" % e)
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
**202** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_my_config**
> UserConfig update_my_config(user_config)

Update my config

Update Current User Configuration.

This endpoint allows an authenticated human user to update their configuration
settings. The new configuration is provided in the request body and will replace
the user's existing settings.

## Request Body:
- **config** (required): An object containing the new configuration settings.

## Response:
- **200 OK**: Returns the updated configuration settings.
- **404 Not Found**: If the user is not found or is not a human user.

## Notes:
- This endpoint is applicable only to human users.

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import iam.v1
from iam.v1.models.user_config import UserConfig
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
    api_instance = iam.v1.UsersApi(api_client)
    user_config = iam.v1.UserConfig() # UserConfig | 

    try:
        # Update my config
        api_response = api_instance.update_my_config(user_config)
        print("The response of UsersApi->update_my_config:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsersApi->update_my_config: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_config** | [**UserConfig**](UserConfig.md)|  | 

### Return type

[**UserConfig**](UserConfig.md)

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

# **update_user_notification_preferences**
> NotificationConfig update_user_notification_preferences(notification_config)

Update user notification preferences

Update Notification Preferences.

This endpoint allows the authenticated user to update their notification
preferences.

## Request Body:
- **config** (required): An object containing the updated notification
preferences.

## Response:
- **200 OK**: Returns the updated notification preferences.
- **404 Not Found**: If the user does not exist.

## Notes:
- Only applicable to human users.

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import iam.v1
from iam.v1.models.notification_config import NotificationConfig
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
    api_instance = iam.v1.UsersApi(api_client)
    notification_config = iam.v1.NotificationConfig() # NotificationConfig | 

    try:
        # Update user notification preferences
        api_response = api_instance.update_user_notification_preferences(notification_config)
        print("The response of UsersApi->update_user_notification_preferences:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsersApi->update_user_notification_preferences: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notification_config** | [**NotificationConfig**](NotificationConfig.md)|  | 

### Return type

[**NotificationConfig**](NotificationConfig.md)

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

