# UpdateApplicant


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**first_name** | **str** |  | [optional] 
**last_name** | **str** |  | [optional] 
**email** | **str** |  | [optional] 
**phone** | **str** |  | [optional] 
**meta** | **object** |  | [optional] 
**physical_guarantors** | [**List[UpdateApplicant]**](UpdateApplicant.md) |  | [optional] [default to []]
**id** | **str** |  | [optional] 

## Example

```python
from core.v2.models.update_applicant import UpdateApplicant

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateApplicant from a JSON string
update_applicant_instance = UpdateApplicant.from_json(json)
# print the JSON string representation of the object
print(UpdateApplicant.to_json())

# convert the object into a dict
update_applicant_dict = update_applicant_instance.to_dict()
# create an instance of UpdateApplicant from a dict
update_applicant_from_dict = UpdateApplicant.from_dict(update_applicant_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


