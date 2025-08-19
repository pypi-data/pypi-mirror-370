# ApplicantLight


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**first_name** | **str** |  | [optional] 
**last_name** | **str** |  | [optional] 
**email** | **str** |  | [optional] 
**score** | **float** |  | [optional] 
**last_update** | **datetime** |  | 
**alerts** | [**List[AlertPretty]**](AlertPretty.md) |  | [optional] [default to []]
**status** | [**StatusB55Enum**](StatusB55Enum.md) |  | 
**is_guarantor** | **bool** |  | [optional] 
**form_submitted** | **datetime** |  | [optional] 

## Example

```python
from core.v1.models.applicant_light import ApplicantLight

# TODO update the JSON string below
json = "{}"
# create an instance of ApplicantLight from a JSON string
applicant_light_instance = ApplicantLight.from_json(json)
# print the JSON string representation of the object
print(ApplicantLight.to_json())

# convert the object into a dict
applicant_light_dict = applicant_light_instance.to_dict()
# create an instance of ApplicantLight from a dict
applicant_light_from_dict = ApplicantLight.from_dict(applicant_light_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


