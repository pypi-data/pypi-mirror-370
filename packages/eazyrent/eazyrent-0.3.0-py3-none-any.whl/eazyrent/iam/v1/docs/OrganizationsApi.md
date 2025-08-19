# iam.v1.OrganizationsApi

All URIs are relative to */iam/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**change_logo**](OrganizationsApi.md#change_logo) | **POST** /organizations/logo/ | Change logo
[**create_linked_account**](OrganizationsApi.md#create_linked_account) | **POST** /organizations/accounts/ | Create linked account
[**delete_logo**](OrganizationsApi.md#delete_logo) | **DELETE** /organizations/logo/ | Delete logo
[**get_alert_importance**](OrganizationsApi.md#get_alert_importance) | **GET** /organizations/alert-importances/ | Get alert importance
[**get_external_references**](OrganizationsApi.md#get_external_references) | **GET** /organizations/external-references/ | Get external references
[**join_organization**](OrganizationsApi.md#join_organization) | **POST** /organizations/join-organization/ | Join organization
[**leave_organization**](OrganizationsApi.md#leave_organization) | **POST** /organizations/leave-organization/ | Leave organization
[**list_all_linked_account**](OrganizationsApi.md#list_all_linked_account) | **GET** /organizations/accounts/ | List all linked account
[**my_organization**](OrganizationsApi.md#my_organization) | **GET** /organizations/me/ | My organization
[**update_alert_importance**](OrganizationsApi.md#update_alert_importance) | **PUT** /organizations/alert-importances/ | Update alert importance
[**update_external_references**](OrganizationsApi.md#update_external_references) | **PUT** /organizations/external-references/ | Update external references


# **change_logo**
> object change_logo(logo, x_eaz_account_id=x_eaz_account_id)

Change logo

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
    api_instance = iam.v1.OrganizationsApi(api_client)
    logo = None # bytearray | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Change logo
        api_response = api_instance.change_logo(logo, x_eaz_account_id=x_eaz_account_id)
        print("The response of OrganizationsApi->change_logo:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrganizationsApi->change_logo: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **logo** | **bytearray**|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

**object**

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader), [OAuth2](../README.md#OAuth2)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_linked_account**
> Organization create_linked_account(create_organization, x_eaz_account_id=x_eaz_account_id)

Create linked account

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
from iam.v1.models.create_organization import CreateOrganization
from iam.v1.models.organization import Organization
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
    api_instance = iam.v1.OrganizationsApi(api_client)
    create_organization = iam.v1.CreateOrganization() # CreateOrganization | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Create linked account
        api_response = api_instance.create_linked_account(create_organization, x_eaz_account_id=x_eaz_account_id)
        print("The response of OrganizationsApi->create_linked_account:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrganizationsApi->create_linked_account: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_organization** | [**CreateOrganization**](CreateOrganization.md)|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

[**Organization**](Organization.md)

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

# **delete_logo**
> object delete_logo(x_eaz_account_id=x_eaz_account_id)

Delete logo

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
    api_instance = iam.v1.OrganizationsApi(api_client)
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Delete logo
        api_response = api_instance.delete_logo(x_eaz_account_id=x_eaz_account_id)
        print("The response of OrganizationsApi->delete_logo:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrganizationsApi->delete_logo: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
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

# **get_alert_importance**
> List[AlertImportance] get_alert_importance(x_eaz_account_id=x_eaz_account_id)

Get alert importance

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
from iam.v1.models.alert_importance import AlertImportance
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
    api_instance = iam.v1.OrganizationsApi(api_client)
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Get alert importance
        api_response = api_instance.get_alert_importance(x_eaz_account_id=x_eaz_account_id)
        print("The response of OrganizationsApi->get_alert_importance:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrganizationsApi->get_alert_importance: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

[**List[AlertImportance]**](AlertImportance.md)

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

# **get_external_references**
> object get_external_references(x_eaz_account_id=x_eaz_account_id)

Get external references

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
    api_instance = iam.v1.OrganizationsApi(api_client)
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Get external references
        api_response = api_instance.get_external_references(x_eaz_account_id=x_eaz_account_id)
        print("The response of OrganizationsApi->get_external_references:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrganizationsApi->get_external_references: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
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

# **join_organization**
> Organization join_organization(join_organization, x_eaz_account_id=x_eaz_account_id)

Join organization

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
from iam.v1.models.join_organization import JoinOrganization
from iam.v1.models.organization import Organization
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
    api_instance = iam.v1.OrganizationsApi(api_client)
    join_organization = iam.v1.JoinOrganization() # JoinOrganization | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Join organization
        api_response = api_instance.join_organization(join_organization, x_eaz_account_id=x_eaz_account_id)
        print("The response of OrganizationsApi->join_organization:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrganizationsApi->join_organization: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **join_organization** | [**JoinOrganization**](JoinOrganization.md)|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

[**Organization**](Organization.md)

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

# **leave_organization**
> Organization leave_organization(x_eaz_account_id=x_eaz_account_id)

Leave organization

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
from iam.v1.models.organization import Organization
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
    api_instance = iam.v1.OrganizationsApi(api_client)
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Leave organization
        api_response = api_instance.leave_organization(x_eaz_account_id=x_eaz_account_id)
        print("The response of OrganizationsApi->leave_organization:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrganizationsApi->leave_organization: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

[**Organization**](Organization.md)

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

# **list_all_linked_account**
> List[ListOrganization] list_all_linked_account()

List all linked account

Returns all linked accounts.

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
import iam.v1
from iam.v1.models.list_organization import ListOrganization
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
    api_instance = iam.v1.OrganizationsApi(api_client)

    try:
        # List all linked account
        api_response = api_instance.list_all_linked_account()
        print("The response of OrganizationsApi->list_all_linked_account:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrganizationsApi->list_all_linked_account: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[ListOrganization]**](ListOrganization.md)

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

# **my_organization**
> Organization my_organization()

My organization

Retrieve the details of the organization associated with the authenticated user.

This endpoint allows the currently authenticated user to retrieve information
about their organization, such as its name, address, and other metadata.

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
import iam.v1
from iam.v1.models.organization import Organization
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
    api_instance = iam.v1.OrganizationsApi(api_client)

    try:
        # My organization
        api_response = api_instance.my_organization()
        print("The response of OrganizationsApi->my_organization:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrganizationsApi->my_organization: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**Organization**](Organization.md)

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

# **update_alert_importance**
> List[AlertImportance] update_alert_importance(alert_importance, x_eaz_account_id=x_eaz_account_id)

Update alert importance

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
from iam.v1.models.alert_importance import AlertImportance
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
    api_instance = iam.v1.OrganizationsApi(api_client)
    alert_importance = [iam.v1.AlertImportance()] # List[AlertImportance] | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Update alert importance
        api_response = api_instance.update_alert_importance(alert_importance, x_eaz_account_id=x_eaz_account_id)
        print("The response of OrganizationsApi->update_alert_importance:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrganizationsApi->update_alert_importance: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **alert_importance** | [**List[AlertImportance]**](AlertImportance.md)|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

[**List[AlertImportance]**](AlertImportance.md)

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

# **update_external_references**
> object update_external_references(request_body, x_eaz_account_id=x_eaz_account_id)

Update external references

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
from iam.v1.models.external_references_value import ExternalReferencesValue
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
    api_instance = iam.v1.OrganizationsApi(api_client)
    request_body = {'key': iam.v1.ExternalReferencesValue()} # Dict[str, ExternalReferencesValue] | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Update external references
        api_response = api_instance.update_external_references(request_body, x_eaz_account_id=x_eaz_account_id)
        print("The response of OrganizationsApi->update_external_references:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrganizationsApi->update_external_references: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | [**Dict[str, ExternalReferencesValue]**](ExternalReferencesValue.md)|  | 
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

