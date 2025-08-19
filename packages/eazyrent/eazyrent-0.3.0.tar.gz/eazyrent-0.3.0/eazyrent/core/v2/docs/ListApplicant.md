# ListApplicant


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**first_name** | **str** |  | [optional] 
**last_name** | **str** |  | [optional] 
**email** | **str** |  | [optional] 
**phone** | **str** |  | [optional] 
**id** | **str** |  | [optional] 
**status** | **str** |  | [optional] [default to 'NEW']
**form_submitted** | **datetime** |  | [optional] 
**score** | **float** |  | [optional] 
**created_at** | **datetime** |  | [optional] 
**updated_at** | **datetime** |  | [optional] 
**is_guarantor** | **bool** |  | [optional] [default to False]
**physical_guarantors** | [**List[ListApplicant]**](ListApplicant.md) |  | [optional] [default to []]
**moral_guarantor** | [**MoralGuarantor**](MoralGuarantor.md) |  | [optional] 
**meta** | **object** |  | [optional] 
**profile** | **str** |  | [optional] 
**completion_rate** | **float** |  | [optional] 
**is_pre_application** | **bool** |  | [optional] [default to False]
**pre_application_validated_at** | **datetime** |  | [optional] 

## Example

```python
from core.v2.models.list_applicant import ListApplicant

# TODO update the JSON string below
json = "{}"
# create an instance of ListApplicant from a JSON string
list_applicant_instance = ListApplicant.from_json(json)
# print the JSON string representation of the object
print(ListApplicant.to_json())

# convert the object into a dict
list_applicant_dict = list_applicant_instance.to_dict()
# create an instance of ListApplicant from a dict
list_applicant_from_dict = ListApplicant.from_dict(list_applicant_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


