# FormComment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**comment** | **str** |  | [optional] 

## Example

```python
from core.v2.models.form_comment import FormComment

# TODO update the JSON string below
json = "{}"
# create an instance of FormComment from a JSON string
form_comment_instance = FormComment.from_json(json)
# print the JSON string representation of the object
print(FormComment.to_json())

# convert the object into a dict
form_comment_dict = form_comment_instance.to_dict()
# create an instance of FormComment from a dict
form_comment_from_dict = FormComment.from_dict(form_comment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


