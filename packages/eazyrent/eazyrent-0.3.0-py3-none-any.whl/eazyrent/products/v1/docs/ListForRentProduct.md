# ListForRentProduct


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
**mandate_type** | **str** | The type of mandate for the property. | [optional] [default to 'management']
**rent_amount** | **float** |  | [optional] 
**monthly_charges** | **float** |  | [optional] 
**furnished** | **bool** | Indicates whether the property is furnished. | [optional] [default to False]
**warranty_amount** | **float** |  | [optional] 
**agency_fees** | **float** |  | [optional] 
**unpaid_rent_insurance** | **bool** |  | [optional] 
**photo** | [**ProductPhoto**](ProductPhoto.md) |  | [optional] 
**incoming_requests** | **int** |  | [optional] [default to 0]

## Example

```python
from products.v1.models.list_for_rent_product import ListForRentProduct

# TODO update the JSON string below
json = "{}"
# create an instance of ListForRentProduct from a JSON string
list_for_rent_product_instance = ListForRentProduct.from_json(json)
# print the JSON string representation of the object
print(ListForRentProduct.to_json())

# convert the object into a dict
list_for_rent_product_dict = list_for_rent_product_instance.to_dict()
# create an instance of ListForRentProduct from a dict
list_for_rent_product_from_dict = ListForRentProduct.from_dict(list_for_rent_product_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


