# PaginatedResponseUnionListForRentProductListForSalesProduct


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** |  | [optional] [default to 0]
**next** | [**Next**](Next.md) |  | [optional] 
**previous** | [**Previous**](Previous.md) |  | [optional] 
**results** | [**List[PaginatedResponseUnionListForRentProductListForSalesProductResultsInner]**](PaginatedResponseUnionListForRentProductListForSalesProductResultsInner.md) |  | [optional] [default to []]

## Example

```python
from products.v1.models.paginated_response_union_list_for_rent_product_list_for_sales_product import PaginatedResponseUnionListForRentProductListForSalesProduct

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResponseUnionListForRentProductListForSalesProduct from a JSON string
paginated_response_union_list_for_rent_product_list_for_sales_product_instance = PaginatedResponseUnionListForRentProductListForSalesProduct.from_json(json)
# print the JSON string representation of the object
print(PaginatedResponseUnionListForRentProductListForSalesProduct.to_json())

# convert the object into a dict
paginated_response_union_list_for_rent_product_list_for_sales_product_dict = paginated_response_union_list_for_rent_product_list_for_sales_product_instance.to_dict()
# create an instance of PaginatedResponseUnionListForRentProductListForSalesProduct from a dict
paginated_response_union_list_for_rent_product_list_for_sales_product_from_dict = PaginatedResponseUnionListForRentProductListForSalesProduct.from_dict(paginated_response_union_list_for_rent_product_list_for_sales_product_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


