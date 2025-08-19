# Product


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
**mandate_type** | **str** | The type of mandate for the property. | [optional] [default to 'management']
**price** | **float** |  | [optional] 
**fee** | **float** |  | [optional] 
**fee_type** | **str** | The type of fee arrangement (e.g., direct or reverse). | [optional] [default to 'direct']
**rent_amount** | **float** |  | [optional] 
**monthly_charges** | **float** |  | [optional] 
**furnished** | **bool** | Indicates whether the property is furnished. | [optional] [default to False]
**warranty_amount** | **float** |  | [optional] 
**agency_fees** | **float** |  | [optional] 
**unpaid_rent_insurance** | **bool** |  | [optional] 

## Example

```python
from products.v1.models.product import Product

# TODO update the JSON string below
json = "{}"
# create an instance of Product from a JSON string
product_instance = Product.from_json(json)
# print the JSON string representation of the object
print(Product.to_json())

# convert the object into a dict
product_dict = product_instance.to_dict()
# create an instance of Product from a dict
product_from_dict = Product.from_dict(product_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


