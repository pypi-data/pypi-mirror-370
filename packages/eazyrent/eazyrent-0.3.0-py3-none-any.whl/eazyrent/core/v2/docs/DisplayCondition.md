# DisplayCondition


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**related_section** | [**RelatedSection**](RelatedSection.md) |  | 
**returns** | [**Returns**](Returns.md) |  | 

## Example

```python
from core.v2.models.display_condition import DisplayCondition

# TODO update the JSON string below
json = "{}"
# create an instance of DisplayCondition from a JSON string
display_condition_instance = DisplayCondition.from_json(json)
# print the JSON string representation of the object
print(DisplayCondition.to_json())

# convert the object into a dict
display_condition_dict = display_condition_instance.to_dict()
# create an instance of DisplayCondition from a dict
display_condition_from_dict = DisplayCondition.from_dict(display_condition_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


