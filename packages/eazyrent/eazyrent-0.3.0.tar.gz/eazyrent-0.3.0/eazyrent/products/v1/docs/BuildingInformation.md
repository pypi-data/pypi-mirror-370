# BuildingInformation

Represents general information about the building, including construction and renovation dates, energy grade, surface area, number of floors, and heating system.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**construction_date** | **date** |  | [optional] 
**renovation_date** | **date** |  | [optional] 
**energy_grade** | **str** |  | [optional] 
**surface** | **float** |  | [optional] 
**floor** | **int** |  | [optional] 
**floors** | **int** |  | [optional] 
**heating_system** | **str** | The type of heating system used in the building. Defaults to &#39;other&#39;. | [optional] [default to 'other']
**rooms** | [**List[RoomSpecification]**](RoomSpecification.md) | A list of specifications for the rooms in the building. Each entry represents a different room. The list is empty if no rooms are specified. | [optional] [default to []]

## Example

```python
from products.v1.models.building_information import BuildingInformation

# TODO update the JSON string below
json = "{}"
# create an instance of BuildingInformation from a JSON string
building_information_instance = BuildingInformation.from_json(json)
# print the JSON string representation of the object
print(BuildingInformation.to_json())

# convert the object into a dict
building_information_dict = building_information_instance.to_dict()
# create an instance of BuildingInformation from a dict
building_information_from_dict = BuildingInformation.from_dict(building_information_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


