# RoomSpecification

Represents the specification of a room within the property, including its name, surface area, orientation, type, and floor.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**surface** | **float** | The surface area of the room in square meters. | 
**orientation** | **str** |  | [optional] 
**type** | **str** |  | [optional] 
**floor** | **int** |  | [optional] 

## Example

```python
from products.v1.models.room_specification import RoomSpecification

# TODO update the JSON string below
json = "{}"
# create an instance of RoomSpecification from a JSON string
room_specification_instance = RoomSpecification.from_json(json)
# print the JSON string representation of the object
print(RoomSpecification.to_json())

# convert the object into a dict
room_specification_dict = room_specification_instance.to_dict()
# create an instance of RoomSpecification from a dict
room_specification_from_dict = RoomSpecification.from_dict(room_specification_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


