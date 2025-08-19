# ForSalesProduct

Public view of Sales product

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
**address** | [**Address**](Address.md) |  | [optional] 
**owner** | **str** |  | [optional] 
**building_information** | [**BuildingInformation**](BuildingInformation.md) |  | [optional] 
**property_facilities** | [**PropertyFacilities**](PropertyFacilities.md) |  | [optional] 
**internal_information** | [**InternalInformation**](InternalInformation.md) |  | [optional] 
**mandate_type** | **str** | The type of mandate for the property. | [optional] [default to 'sales']
**price** | **float** |  | [optional] 
**fee** | **float** |  | [optional] 
**fee_type** | **str** | The type of fee arrangement (e.g., direct or reverse). | [optional] [default to 'direct']
**id** | **str** |  | [optional] 
**tenant** | **str** |  | 
**created_at** | **datetime** |  | [optional] 
**updated_at** | **datetime** |  | [optional] 
**photo** | [**ProductPhoto**](ProductPhoto.md) |  | [optional] 

## Example

```python
from products.v1.models.for_sales_product import ForSalesProduct

# TODO update the JSON string below
json = "{}"
# create an instance of ForSalesProduct from a JSON string
for_sales_product_instance = ForSalesProduct.from_json(json)
# print the JSON string representation of the object
print(ForSalesProduct.to_json())

# convert the object into a dict
for_sales_product_dict = for_sales_product_instance.to_dict()
# create an instance of ForSalesProduct from a dict
for_sales_product_from_dict = ForSalesProduct.from_dict(for_sales_product_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


