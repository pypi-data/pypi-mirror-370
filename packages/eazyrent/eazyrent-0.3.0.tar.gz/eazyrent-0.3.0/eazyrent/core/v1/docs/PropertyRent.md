# PropertyRent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**title** | **str** |  | 
**reference** | **str** |  | [optional] 
**rent_amount** | **float** |  | 
**unpaid_rent_insurance** | **bool** |  | [optional] 
**added_at** | **datetime** |  | 
**last_update** | **datetime** |  | 
**company** | [**Company**](Company.md) |  | 
**disable_spontaneous_applications** | **bool** |  | [optional] 

## Example

```python
from core.v1.models.property_rent import PropertyRent

# TODO update the JSON string below
json = "{}"
# create an instance of PropertyRent from a JSON string
property_rent_instance = PropertyRent.from_json(json)
# print the JSON string representation of the object
print(PropertyRent.to_json())

# convert the object into a dict
property_rent_dict = property_rent_instance.to_dict()
# create an instance of PropertyRent from a dict
property_rent_from_dict = PropertyRent.from_dict(property_rent_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


