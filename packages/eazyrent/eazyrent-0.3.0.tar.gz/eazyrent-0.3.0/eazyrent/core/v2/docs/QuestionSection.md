# QuestionSection


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**title** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**component** | **str** |  | [optional] [default to 'QuestionSection']
**mandatory** | **bool** |  | [optional] [default to False]
**display_condition** | [**DisplayCondition**](DisplayCondition.md) |  | [optional] 
**question** | **str** |  | 
**options** | **List[str]** |  | [optional] 
**completed** | **bool** |  | [optional] [default to False]
**response** | **str** |  | [optional] 
**display** | **bool** |  | [optional] [default to True]

## Example

```python
from core.v2.models.question_section import QuestionSection

# TODO update the JSON string below
json = "{}"
# create an instance of QuestionSection from a JSON string
question_section_instance = QuestionSection.from_json(json)
# print the JSON string representation of the object
print(QuestionSection.to_json())

# convert the object into a dict
question_section_dict = question_section_instance.to_dict()
# create an instance of QuestionSection from a dict
question_section_from_dict = QuestionSection.from_dict(question_section_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


