# PropertyRentPartialUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **str** |  | [optional] 
**reference** | **str** |  | [optional] 
**rent_amount** | **float** |  | [optional] 
**unpaid_rent_insurance** | **bool** |  | [optional] 
**disable_spontaneous_applications** | **bool** |  | [optional] 

## Example

```python
from core.v1.models.property_rent_partial_update import PropertyRentPartialUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of PropertyRentPartialUpdate from a JSON string
property_rent_partial_update_instance = PropertyRentPartialUpdate.from_json(json)
# print the JSON string representation of the object
print(PropertyRentPartialUpdate.to_json())

# convert the object into a dict
property_rent_partial_update_dict = property_rent_partial_update_instance.to_dict()
# create an instance of PropertyRentPartialUpdate from a dict
property_rent_partial_update_from_dict = PropertyRentPartialUpdate.from_dict(property_rent_partial_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


