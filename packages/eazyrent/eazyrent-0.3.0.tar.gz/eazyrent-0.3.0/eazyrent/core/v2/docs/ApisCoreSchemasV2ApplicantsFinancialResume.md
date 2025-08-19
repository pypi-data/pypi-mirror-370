# ApisCoreSchemasV2ApplicantsFinancialResume


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**payslip_incomes** | **float** |  | [optional] 
**taxnotice_incomes** | **float** |  | [optional] 
**wages** | [**List[Wage]**](Wage.md) |  | [optional] 
**estimated_incomes** | **float** |  | [optional] 
**estimated_solvency** | **float** |  | [optional] 

## Example

```python
from core.v2.models.apis_core_schemas_v2_applicants_financial_resume import ApisCoreSchemasV2ApplicantsFinancialResume

# TODO update the JSON string below
json = "{}"
# create an instance of ApisCoreSchemasV2ApplicantsFinancialResume from a JSON string
apis_core_schemas_v2_applicants_financial_resume_instance = ApisCoreSchemasV2ApplicantsFinancialResume.from_json(json)
# print the JSON string representation of the object
print(ApisCoreSchemasV2ApplicantsFinancialResume.to_json())

# convert the object into a dict
apis_core_schemas_v2_applicants_financial_resume_dict = apis_core_schemas_v2_applicants_financial_resume_instance.to_dict()
# create an instance of ApisCoreSchemasV2ApplicantsFinancialResume from a dict
apis_core_schemas_v2_applicants_financial_resume_from_dict = ApisCoreSchemasV2ApplicantsFinancialResume.from_dict(apis_core_schemas_v2_applicants_financial_resume_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


