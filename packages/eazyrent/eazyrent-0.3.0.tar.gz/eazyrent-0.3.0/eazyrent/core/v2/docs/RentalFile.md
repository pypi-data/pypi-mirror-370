# RentalFile


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**product_id** | **str** |  | [optional] 
**meta** | **object** |  | [optional] 
**allow_user_engagement** | **bool** | If enabled, applicants will be able to access their data, and the system will allow email sending | [optional] [default to True]
**id** | **str** |  | 
**status** | **str** |  | [optional] [default to 'NEW']
**applicants_situation** | **str** |  | [optional] 
**archived_at** | **datetime** |  | [optional] 
**tags** | [**List[Tag]**](Tag.md) |  | [optional] [default to []]
**managers** | **List[str]** |  | [optional] [default to []]
**created_at** | **datetime** |  | [optional] 
**updated_at** | **datetime** |  | [optional] 
**score** | **float** |  | [optional] 
**completion_rate** | **float** |  | [optional] 
**applicants** | [**List[Applicant]**](Applicant.md) |  | 
**decision** | **str** |  | [optional] [default to 'PENDING']
**product** | [**ListProductsProjection**](ListProductsProjection.md) |  | [optional] 
**is_pre_application** | **bool** |  | [optional] [default to False]
**pre_application_validated_at** | **datetime** |  | [optional] 
**comments** | [**List[RentalFileComment]**](RentalFileComment.md) |  | [optional] [default to []]
**analysis_required_at** | **datetime** |  | [optional] 
**financial_resume** | [**ApisCoreSchemasV2RentalFilesFinancialResume**](ApisCoreSchemasV2RentalFilesFinancialResume.md) |  | [optional] 

## Example

```python
from core.v2.models.rental_file import RentalFile

# TODO update the JSON string below
json = "{}"
# create an instance of RentalFile from a JSON string
rental_file_instance = RentalFile.from_json(json)
# print the JSON string representation of the object
print(RentalFile.to_json())

# convert the object into a dict
rental_file_dict = rental_file_instance.to_dict()
# create an instance of RentalFile from a dict
rental_file_from_dict = RentalFile.from_dict(rental_file_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


