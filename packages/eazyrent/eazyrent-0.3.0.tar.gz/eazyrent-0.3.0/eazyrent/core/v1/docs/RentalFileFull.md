# RentalFileFull


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**status** | [**StatusD7bEnum**](StatusD7bEnum.md) |  | [optional] 
**property_rent** | [**PropertyRentList**](PropertyRentList.md) |  | [optional] 
**applicants** | [**List[ApplicantList]**](ApplicantList.md) |  | 
**created_at** | **datetime** |  | 
**last_update** | **datetime** |  | 
**manager** | **str** |  | [optional] 
**manager_name** | **str** |  | [optional] 
**applicants_situation** | [**ApplicantsSituationEnum**](ApplicantsSituationEnum.md) |  | [optional] 
**tags** | **List[str]** |  | [optional] 
**reference** | **str** |  | [optional] 
**form_completion** | **float** |  | [optional] 

## Example

```python
from core.v1.models.rental_file_full import RentalFileFull

# TODO update the JSON string below
json = "{}"
# create an instance of RentalFileFull from a JSON string
rental_file_full_instance = RentalFileFull.from_json(json)
# print the JSON string representation of the object
print(RentalFileFull.to_json())

# convert the object into a dict
rental_file_full_dict = rental_file_full_instance.to_dict()
# create an instance of RentalFileFull from a dict
rental_file_full_from_dict = RentalFileFull.from_dict(rental_file_full_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


