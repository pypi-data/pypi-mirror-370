# Applicant


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
**physical_guarantors** | [**List[Applicant]**](Applicant.md) |  | [optional] [default to []]
**moral_guarantor** | [**MoralGuarantor**](MoralGuarantor.md) |  | [optional] 
**meta** | **object** |  | [optional] 
**profile** | **str** |  | [optional] 
**completion_rate** | **float** |  | [optional] 
**is_pre_application** | **bool** |  | [optional] [default to False]
**pre_application_validated_at** | **datetime** |  | [optional] 
**documents** | [**List[ListDocument]**](ListDocument.md) |  | [optional] [default to []]
**financial_resume** | [**ApisCoreSchemasV2ApplicantsFinancialResume**](ApisCoreSchemasV2ApplicantsFinancialResume.md) |  | [optional] 
**form_available** | **bool** | If applicant has a form associated | [optional] [default to False]
**external_data** | [**ExternalData**](ExternalData.md) |  | [optional] 

## Example

```python
from core.v2.models.applicant import Applicant

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


