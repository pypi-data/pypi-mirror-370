# ApplicantList


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**first_name** | **str** |  | [optional] 
**last_name** | **str** |  | [optional] 
**email** | **str** |  | [optional] 
**phone** | **str** |  | [optional] 
**is_guarantor** | **bool** |  | [optional] 
**added_at** | **datetime** |  | [optional] 
**last_update** | **datetime** |  | [optional] 
**status** | [**StatusB55Enum**](StatusB55Enum.md) |  | [optional] 
**score** | **float** |  | [optional] 
**form_submitted** | **datetime** |  | [optional] 

## Example

```python
from core.v1.models.applicant_list import ApplicantList

# TODO update the JSON string below
json = "{}"
# create an instance of ApplicantList from a JSON string
applicant_list_instance = ApplicantList.from_json(json)
# print the JSON string representation of the object
print(ApplicantList.to_json())

# convert the object into a dict
applicant_list_dict = applicant_list_instance.to_dict()
# create an instance of ApplicantList from a dict
applicant_list_from_dict = ApplicantList.from_dict(applicant_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


