# Applicant


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**physical_guarantors** | [**List[ApisCoreSchemasV1ApplicantsPhysicalGuarantor]**](ApisCoreSchemasV1ApplicantsPhysicalGuarantor.md) |  | [optional] [default to []]
**alerts** | [**List[AlertPretty]**](AlertPretty.md) |  | [optional] [default to []]
**score** | **float** |  | [optional] 
**first_name** | **str** |  | [optional] 
**last_name** | **str** |  | [optional] 
**email** | **str** |  | [optional] 
**phone** | **str** |  | [optional] 
**external_reference** | **str** |  | [optional] 
**added_at** | **datetime** |  | [optional] 
**last_update** | **datetime** |  | [optional] 
**is_guarantor** | **bool** |  | [optional] 
**status** | [**StatusB55Enum**](StatusB55Enum.md) |  | 
**applicant_file** | **str** |  | [optional] 
**category** | **str** |  | [optional] 
**form_submitted** | **datetime** |  | [optional] 

## Example

```python
from core.v1.models.applicant import Applicant

# TODO update the JSON string below
json = "{}"
# create an instance of Applicant from a JSON string
applicant_instance = Applicant.from_json(json)
# print the JSON string representation of the object
print(Applicant.to_json())

# convert the object into a dict
applicant_dict = applicant_instance.to_dict()
# create an instance of Applicant from a dict
applicant_from_dict = Applicant.from_dict(applicant_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


