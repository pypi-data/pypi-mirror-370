# RentalFilePartialUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**property_rent** | **str** |  | [optional] 
**applicants_situation** | [**ApplicantsSituationEnum**](ApplicantsSituationEnum.md) |  | [optional] 
**reference** | **str** |  | [optional] 

## Example

```python
from core.v1.models.rental_file_partial_update import RentalFilePartialUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of RentalFilePartialUpdate from a JSON string
rental_file_partial_update_instance = RentalFilePartialUpdate.from_json(json)
# print the JSON string representation of the object
print(RentalFilePartialUpdate.to_json())

# convert the object into a dict
rental_file_partial_update_dict = rental_file_partial_update_instance.to_dict()
# create an instance of RentalFilePartialUpdate from a dict
rental_file_partial_update_from_dict = RentalFilePartialUpdate.from_dict(rental_file_partial_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


