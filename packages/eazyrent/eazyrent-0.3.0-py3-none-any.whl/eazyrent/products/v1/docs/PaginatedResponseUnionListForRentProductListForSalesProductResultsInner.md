# PaginatedResponseUnionListForRentProductListForSalesProductResultsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**achived_at** | **datetime** |  | [optional] 
**category** | [**ProductType**](ProductType.md) |  | [optional] 
**title** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**reference** | **str** |  | [optional] 
**available** | **bool** | Indicates whether the property is currently available. | [optional] [default to True]
**availability** | **date** |  | [optional] 
**exclusivity** | **bool** |  | [optional] 
**disable_spontaneous_applications** | **bool** |  | [optional] 
**managers** | **List[str]** |  | [optional] [default to []]
**meta** | **object** |  | [optional] 
**id** | **str** |  | 
**tenant** | **str** |  | 
**created_at** | **datetime** |  | 
**updated_at** | **datetime** |  | 
**mandate_type** | **str** | The type of mandate for the property. | [optional] [default to 'sales']
**rent_amount** | **float** |  | [optional] 
**monthly_charges** | **float** |  | [optional] 
**furnished** | **bool** | Indicates whether the property is furnished. | [optional] [default to False]
**warranty_amount** | **float** |  | [optional] 
**agency_fees** | **float** |  | [optional] 
**unpaid_rent_insurance** | **bool** |  | [optional] 
**photo** | [**ProductPhoto**](ProductPhoto.md) |  | [optional] 
**incoming_requests** | **int** |  | [optional] [default to 0]
**price** | **float** |  | [optional] 
**fee** | **float** |  | [optional] 
**fee_type** | **str** | The type of fee arrangement (e.g., direct or reverse). | [optional] [default to 'direct']

## Example

```python
from products.v1.models.paginated_response_union_list_for_rent_product_list_for_sales_product_results_inner import PaginatedResponseUnionListForRentProductListForSalesProductResultsInner

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResponseUnionListForRentProductListForSalesProductResultsInner from a JSON string
paginated_response_union_list_for_rent_product_list_for_sales_product_results_inner_instance = PaginatedResponseUnionListForRentProductListForSalesProductResultsInner.from_json(json)
# print the JSON string representation of the object
print(PaginatedResponseUnionListForRentProductListForSalesProductResultsInner.to_json())

# convert the object into a dict
paginated_response_union_list_for_rent_product_list_for_sales_product_results_inner_dict = paginated_response_union_list_for_rent_product_list_for_sales_product_results_inner_instance.to_dict()
# create an instance of PaginatedResponseUnionListForRentProductListForSalesProductResultsInner from a dict
paginated_response_union_list_for_rent_product_list_for_sales_product_results_inner_from_dict = PaginatedResponseUnionListForRentProductListForSalesProductResultsInner.from_dict(paginated_response_union_list_for_rent_product_list_for_sales_product_results_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


