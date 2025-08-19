# MarkdownSection


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**title** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**component** | **str** |  | [optional] [default to 'Markdown']
**mandatory** | **bool** |  | [optional] [default to False]
**display_condition** | [**DisplayCondition**](DisplayCondition.md) |  | [optional] 
**content** | **str** |  | 
**display** | **bool** |  | [optional] [default to True]
**completed** | **bool** |  | [optional] [default to True]

## Example

```python
from core.v2.models.markdown_section import MarkdownSection

# TODO update the JSON string below
json = "{}"
# create an instance of MarkdownSection from a JSON string
markdown_section_instance = MarkdownSection.from_json(json)
# print the JSON string representation of the object
print(MarkdownSection.to_json())

# convert the object into a dict
markdown_section_dict = markdown_section_instance.to_dict()
# create an instance of MarkdownSection from a dict
markdown_section_from_dict = MarkdownSection.from_dict(markdown_section_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


