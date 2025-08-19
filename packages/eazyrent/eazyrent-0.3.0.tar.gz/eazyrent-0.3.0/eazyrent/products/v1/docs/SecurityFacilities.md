# SecurityFacilities

Represents the security facilities available in a property, including features such as concierge service, security guard presence, cameras, alarm systems, and armored doors.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**concierge** | **bool** |  | [optional] 
**security_guard** | **bool** |  | [optional] 
**camera** | **bool** |  | [optional] 
**alarm_system** | **bool** |  | [optional] 
**armored_door** | **bool** |  | [optional] 

## Example

```python
from products.v1.models.security_facilities import SecurityFacilities

# TODO update the JSON string below
json = "{}"
# create an instance of SecurityFacilities from a JSON string
security_facilities_instance = SecurityFacilities.from_json(json)
# print the JSON string representation of the object
print(SecurityFacilities.to_json())

# convert the object into a dict
security_facilities_dict = security_facilities_instance.to_dict()
# create an instance of SecurityFacilities from a dict
security_facilities_from_dict = SecurityFacilities.from_dict(security_facilities_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


