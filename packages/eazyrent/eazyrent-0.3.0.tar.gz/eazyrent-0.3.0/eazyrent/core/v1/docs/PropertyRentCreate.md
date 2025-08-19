# PropertyRentCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **str** |  | 
**reference** | **str** |  | [optional] 
**rent_amount** | **float** |  | 
**unpaid_rent_insurance** | **bool** |  | [optional] 
**disable_spontaneous_applications** | **bool** |  | [optional] 

## Example

```python
from core.v1.models.property_rent_create import PropertyRentCreate

# TODO update the JSON string below
json = "{}"
# create an instance of PropertyRentCreate from a JSON string
property_rent_create_instance = PropertyRentCreate.from_json(json)
# print the JSON string representation of the object
print(PropertyRentCreate.to_json())

# convert the object into a dict
property_rent_create_dict = property_rent_create_instance.to_dict()
# create an instance of PropertyRentCreate from a dict
property_rent_create_from_dict = PropertyRentCreate.from_dict(property_rent_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


