# FormPart


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **str** |  | 
**component** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**sections** | [**List[FormPartSectionsInner]**](FormPartSectionsInner.md) |  | [optional] [default to []]
**display_condition** | [**DisplayCondition**](DisplayCondition.md) |  | [optional] 
**completed** | **bool** |  | [optional] [default to False]
**component_data** | **object** |  | [optional] 
**display** | **bool** |  | [optional] [default to True]

## Example

```python
from core.v2.models.form_part import FormPart

# TODO update the JSON string below
json = "{}"
# create an instance of FormPart from a JSON string
form_part_instance = FormPart.from_json(json)
# print the JSON string representation of the object
print(FormPart.to_json())

# convert the object into a dict
form_part_dict = form_part_instance.to_dict()
# create an instance of FormPart from a dict
form_part_from_dict = FormPart.from_dict(form_part_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


