# RentalFile


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**status** | [**StatusD7bEnum**](StatusD7bEnum.md) |  | 
**score** | **float** |  | [optional] 
**form_completion** | **float** |  | [optional] 
**ttl** | **str** |  | [optional] 
**created_at** | **datetime** |  | 
**last_update** | **datetime** |  | 
**property_rent** | **str** |  | [optional] 
**applicants** | [**List[ApplicantLight]**](ApplicantLight.md) |  | [optional] [default to []]
**applicants_situation** | [**ApplicantsSituationEnum**](ApplicantsSituationEnum.md) |  | [optional] 
**manager** | **str** |  | [optional] 
**manager_name** | **str** |  | [optional] 
**reference** | **str** |  | [optional] 

## Example

```python
from core.v1.models.rental_file import RentalFile

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


