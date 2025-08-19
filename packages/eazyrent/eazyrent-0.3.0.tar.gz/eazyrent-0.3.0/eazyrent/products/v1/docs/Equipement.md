# Equipement

Represents additional equipment in the property with a name and description.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the equipment, such as &#39;Washing Machine&#39; or &#39;Coffee Maker&#39;. | 
**description** | **str** | A description of the equipment and its function. | 

## Example

```python
from products.v1.models.equipement import Equipement

# TODO update the JSON string below
json = "{}"
# create an instance of Equipement from a JSON string
equipement_instance = Equipement.from_json(json)
# print the JSON string representation of the object
print(Equipement.to_json())

# convert the object into a dict
equipement_dict = equipement_instance.to_dict()
# create an instance of Equipement from a dict
equipement_from_dict = Equipement.from_dict(equipement_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


