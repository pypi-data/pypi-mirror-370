# AirConditioning

Represents an air conditioning system with details about installation, number of splits, number of units, and the last maintenance date.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**installation_date** | **date** |  | [optional] 
**split_number** | **int** | The number of splits in the air conditioning system. A split refers to the separate sections of the system. The default is 1. | [optional] [default to 1]
**units_number** | **int** | The number of individual units in the air conditioning system. The default is 1. | [optional] [default to 1]
**last_maintenance_date** | **date** |  | [optional] 

## Example

```python
from products.v1.models.air_conditioning import AirConditioning

# TODO update the JSON string below
json = "{}"
# create an instance of AirConditioning from a JSON string
air_conditioning_instance = AirConditioning.from_json(json)
# print the JSON string representation of the object
print(AirConditioning.to_json())

# convert the object into a dict
air_conditioning_dict = air_conditioning_instance.to_dict()
# create an instance of AirConditioning from a dict
air_conditioning_from_dict = AirConditioning.from_dict(air_conditioning_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


