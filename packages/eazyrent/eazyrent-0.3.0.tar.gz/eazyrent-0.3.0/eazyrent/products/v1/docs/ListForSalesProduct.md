# ListForSalesProduct


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
**price** | **float** |  | [optional] 
**fee** | **float** |  | [optional] 
**fee_type** | **str** | The type of fee arrangement (e.g., direct or reverse). | [optional] [default to 'direct']
**photo** | [**ProductPhoto**](ProductPhoto.md) |  | [optional] 
**incoming_requests** | **int** |  | [optional] [default to 0]

## Example

```python
from products.v1.models.list_for_sales_product import ListForSalesProduct

# TODO update the JSON string below
json = "{}"
# create an instance of ListForSalesProduct from a JSON string
list_for_sales_product_instance = ListForSalesProduct.from_json(json)
# print the JSON string representation of the object
print(ListForSalesProduct.to_json())

# convert the object into a dict
list_for_sales_product_dict = list_for_sales_product_instance.to_dict()
# create an instance of ListForSalesProduct from a dict
list_for_sales_product_from_dict = ListForSalesProduct.from_dict(list_for_sales_product_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


