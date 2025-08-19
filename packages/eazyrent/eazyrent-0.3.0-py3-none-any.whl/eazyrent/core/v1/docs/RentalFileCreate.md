# RentalFileCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**property_rent** | **str** |  | 
**applicants_situation** | [**ApplicantsSituationEnum**](ApplicantsSituationEnum.md) |  | 
**reference** | **str** |  | [optional] 

## Example

```python
from core.v1.models.rental_file_create import RentalFileCreate

# TODO update the JSON string below
json = "{}"
# create an instance of RentalFileCreate from a JSON string
rental_file_create_instance = RentalFileCreate.from_json(json)
# print the JSON string representation of the object
print(RentalFileCreate.to_json())

# convert the object into a dict
rental_file_create_dict = rental_file_create_instance.to_dict()
# create an instance of RentalFileCreate from a dict
rental_file_create_from_dict = RentalFileCreate.from_dict(rental_file_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


