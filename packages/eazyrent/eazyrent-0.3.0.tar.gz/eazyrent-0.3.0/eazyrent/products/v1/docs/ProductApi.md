# products.v1.ProductApi

All URIs are relative to */products/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_product**](ProductApi.md#create_product) | **POST** /products/ | Create product
[**delete_product**](ProductApi.md#delete_product) | **DELETE** /products/{id}/ | Delete product
[**get_product**](ProductApi.md#get_product) | **GET** /products/{id}/ | Get product
[**list_products**](ProductApi.md#list_products) | **GET** /products/ | List products
[**partial_update_product**](ProductApi.md#partial_update_product) | **PATCH** /products/{id}/ | Partial update product
[**update_product**](ProductApi.md#update_product) | **PUT** /products/{id}/ | Update product


# **create_product**
> ResponseCreateProduct create_product(product, x_eaz_account_id=x_eaz_account_id)

Create product

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
- `product:write`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import products.v1
from products.v1.models.product import Product
from products.v1.models.response_create_product import ResponseCreateProduct
from products.v1.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /products/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = products.v1.Configuration(
    host = "/products/v1"
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
with products.v1.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = products.v1.ProductApi(api_client)
    product = products.v1.Product() # Product | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Create product
        api_response = api_instance.create_product(product, x_eaz_account_id=x_eaz_account_id)
        print("The response of ProductApi->create_product:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProductApi->create_product: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **product** | [**Product**](Product.md)|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

[**ResponseCreateProduct**](ResponseCreateProduct.md)

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

# **delete_product**
> delete_product(id, cascade=cascade, x_eaz_account_id=x_eaz_account_id)

Delete product

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
- `product:write`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import products.v1
from products.v1.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /products/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = products.v1.Configuration(
    host = "/products/v1"
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
with products.v1.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = products.v1.ProductApi(api_client)
    id = 'id_example' # str | 
    cascade = False # bool |  (optional) (default to False)
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Delete product
        api_instance.delete_product(id, cascade=cascade, x_eaz_account_id=x_eaz_account_id)
    except Exception as e:
        print("Exception when calling ProductApi->delete_product: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **cascade** | **bool**|  | [optional] [default to False]
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

# **get_product**
> ResponseGetProduct get_product(id, x_eaz_account_id=x_eaz_account_id)

Get product

Detail

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
- `product:read`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import products.v1
from products.v1.models.response_get_product import ResponseGetProduct
from products.v1.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /products/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = products.v1.Configuration(
    host = "/products/v1"
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
with products.v1.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = products.v1.ProductApi(api_client)
    id = 'id_example' # str | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Get product
        api_response = api_instance.get_product(id, x_eaz_account_id=x_eaz_account_id)
        print("The response of ProductApi->get_product:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProductApi->get_product: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

[**ResponseGetProduct**](ResponseGetProduct.md)

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

# **list_products**
> PaginatedResponseUnionListForRentProductListForSalesProduct list_products(order_by=order_by, limit=limit, offset=offset, search=search, category=category, managers__in=managers__in, managers__nin=managers__nin, managers__eq=managers__eq, available=available, mandate_type=mandate_type, created_at__lte=created_at__lte, created_at__gte=created_at__gte, updated_at__lte=updated_at__lte, updated_at__gte=updated_at__gte, price__gte=price__gte, price__lte=price__lte, archived__lte=archived__lte, archived__gte=archived__gte, x_eaz_account_id=x_eaz_account_id)

List products

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
- `product:read`

## 📄 Pagination

This endpoint uses pagination with `limit` and `offset`.

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import products.v1
from products.v1.models.mandate_type import MandateType
from products.v1.models.paginated_response_union_list_for_rent_product_list_for_sales_product import PaginatedResponseUnionListForRentProductListForSalesProduct
from products.v1.models.product_type import ProductType
from products.v1.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /products/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = products.v1.Configuration(
    host = "/products/v1"
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
with products.v1.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = products.v1.ProductApi(api_client)
    order_by = -created_at # str |  (optional) (default to -created_at)
    limit = 10 # int |  (optional) (default to 10)
    offset = 0 # int |  (optional) (default to 0)
    search = 'search_example' # str |  (optional)
    category = products.v1.ProductType() # ProductType |  (optional)
    managers__in = 'managers__in_example' # str |  (optional)
    managers__nin = 'managers__nin_example' # str |  (optional)
    managers__eq = products.v1.ManagersEq() # ManagersEq |  (optional)
    available = True # bool |  (optional)
    mandate_type = products.v1.MandateType() # MandateType |  (optional)
    created_at__lte = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    created_at__gte = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    updated_at__lte = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    updated_at__gte = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    price__gte = 3.4 # float |  (optional)
    price__lte = 3.4 # float |  (optional)
    archived__lte = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    archived__gte = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # List products
        api_response = api_instance.list_products(order_by=order_by, limit=limit, offset=offset, search=search, category=category, managers__in=managers__in, managers__nin=managers__nin, managers__eq=managers__eq, available=available, mandate_type=mandate_type, created_at__lte=created_at__lte, created_at__gte=created_at__gte, updated_at__lte=updated_at__lte, updated_at__gte=updated_at__gte, price__gte=price__gte, price__lte=price__lte, archived__lte=archived__lte, archived__gte=archived__gte, x_eaz_account_id=x_eaz_account_id)
        print("The response of ProductApi->list_products:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProductApi->list_products: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **order_by** | **str**|  | [optional] [default to -created_at]
 **limit** | **int**|  | [optional] [default to 10]
 **offset** | **int**|  | [optional] [default to 0]
 **search** | **str**|  | [optional] 
 **category** | [**ProductType**](.md)|  | [optional] 
 **managers__in** | **str**|  | [optional] 
 **managers__nin** | **str**|  | [optional] 
 **managers__eq** | [**ManagersEq**](.md)|  | [optional] 
 **available** | **bool**|  | [optional] 
 **mandate_type** | [**MandateType**](.md)|  | [optional] 
 **created_at__lte** | **datetime**|  | [optional] 
 **created_at__gte** | **datetime**|  | [optional] 
 **updated_at__lte** | **datetime**|  | [optional] 
 **updated_at__gte** | **datetime**|  | [optional] 
 **price__gte** | **float**|  | [optional] 
 **price__lte** | **float**|  | [optional] 
 **archived__lte** | **datetime**|  | [optional] 
 **archived__gte** | **datetime**|  | [optional] 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

[**PaginatedResponseUnionListForRentProductListForSalesProduct**](PaginatedResponseUnionListForRentProductListForSalesProduct.md)

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

# **partial_update_product**
> ResponsePartialUpdateProduct partial_update_product(id, update_product, x_eaz_account_id=x_eaz_account_id)

Partial update product

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
- `product:write`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import products.v1
from products.v1.models.response_partial_update_product import ResponsePartialUpdateProduct
from products.v1.models.update_product import UpdateProduct
from products.v1.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /products/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = products.v1.Configuration(
    host = "/products/v1"
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
with products.v1.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = products.v1.ProductApi(api_client)
    id = 'id_example' # str | 
    update_product = products.v1.UpdateProduct() # UpdateProduct | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Partial update product
        api_response = api_instance.partial_update_product(id, update_product, x_eaz_account_id=x_eaz_account_id)
        print("The response of ProductApi->partial_update_product:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProductApi->partial_update_product: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **update_product** | [**UpdateProduct**](UpdateProduct.md)|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

[**ResponsePartialUpdateProduct**](ResponsePartialUpdateProduct.md)

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

# **update_product**
> ResponseUpdateProduct update_product(id, update_product, x_eaz_account_id=x_eaz_account_id)

Update product

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
- `product:write`

### Example

* Api Key Authentication (APIKeyHeader):
* OAuth Authentication (OAuth2):

```python
import products.v1
from products.v1.models.response_update_product import ResponseUpdateProduct
from products.v1.models.update_product import UpdateProduct
from products.v1.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /products/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = products.v1.Configuration(
    host = "/products/v1"
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
with products.v1.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = products.v1.ProductApi(api_client)
    id = 'id_example' # str | 
    update_product = products.v1.UpdateProduct() # UpdateProduct | 
    x_eaz_account_id = 'x_eaz_account_id_example' # str | The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. (optional)

    try:
        # Update product
        api_response = api_instance.update_product(id, update_product, x_eaz_account_id=x_eaz_account_id)
        print("The response of ProductApi->update_product:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProductApi->update_product: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **update_product** | [**UpdateProduct**](UpdateProduct.md)|  | 
 **x_eaz_account_id** | **str**| The default is always the organization of the requesting user. If you like to get/set a result of another organization include the header. Make sure the user has permission to access the requested data. | [optional] 

### Return type

[**ResponseUpdateProduct**](ResponseUpdateProduct.md)

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

