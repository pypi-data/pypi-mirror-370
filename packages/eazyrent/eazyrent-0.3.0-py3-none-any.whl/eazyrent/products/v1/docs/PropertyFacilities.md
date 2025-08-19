# PropertyFacilities

Represents the facilities available in a property, including air conditioning, pool specifications, garage, terraces, cellars, gardens, internet access, additional equipment, intercom, elevator, and parking details.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**air_conditioning** | [**AirConditioning**](AirConditioning.md) |  | [optional] 
**pool** | [**PoolSpecification**](PoolSpecification.md) |  | [optional] 
**garage** | [**List[RoomSpecification]**](RoomSpecification.md) | A list of specifications for the property&#39;s garage(s). Each entry in the list represents a different garage. The list is empty if there are no garages. | [optional] [default to []]
**terraces** | [**List[RoomSpecification]**](RoomSpecification.md) | A list of specifications for the property&#39;s terrace(s). Each entry in the list represents a different terrace. The list is empty if there are no terraces. | [optional] [default to []]
**cellars** | [**List[RoomSpecification]**](RoomSpecification.md) | A list of specifications for the property&#39;s cellar(s). Each entry in the list represents a different cellar. The list is empty if there are no cellars. | [optional] [default to []]
**gardens** | [**List[RoomSpecification]**](RoomSpecification.md) | A list of specifications for the property&#39;s garden(s). Each entry in the list represents a different garden. The list is empty if there are no gardens. | [optional] [default to []]
**internet_access** | **str** |  | [optional] 
**others** | [**List[Equipement]**](Equipement.md) | A list of other equipment available in the property. Each entry in the list represents a different piece of equipment. The list is empty if there are no additional equipment details. | [optional] [default to []]
**intercom** | **bool** |  | [optional] 
**elevator** | **bool** |  | [optional] 
**parking** | **int** | The number of parking spaces available at the property. The default is 0. | [optional] [default to 0]
**security_facilities** | [**SecurityFacilities**](SecurityFacilities.md) |  | [optional] 

## Example

```python
from products.v1.models.property_facilities import PropertyFacilities

# TODO update the JSON string below
json = "{}"
# create an instance of PropertyFacilities from a JSON string
property_facilities_instance = PropertyFacilities.from_json(json)
# print the JSON string representation of the object
print(PropertyFacilities.to_json())

# convert the object into a dict
property_facilities_dict = property_facilities_instance.to_dict()
# create an instance of PropertyFacilities from a dict
property_facilities_from_dict = PropertyFacilities.from_dict(property_facilities_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


