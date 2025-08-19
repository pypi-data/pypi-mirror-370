# MoralGuarantor


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**file_path** | **str** |  | 
**type** | **str** |  | 
**created_at** | **datetime** |  | 
**updated_at** | **datetime** |  | 

## Example

```python
from core.v2.models.moral_guarantor import MoralGuarantor

# TODO update the JSON string below
json = "{}"
# create an instance of MoralGuarantor from a JSON string
moral_guarantor_instance = MoralGuarantor.from_json(json)
# print the JSON string representation of the object
print(MoralGuarantor.to_json())

# convert the object into a dict
moral_guarantor_dict = moral_guarantor_instance.to_dict()
# create an instance of MoralGuarantor from a dict
moral_guarantor_from_dict = MoralGuarantor.from_dict(moral_guarantor_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


