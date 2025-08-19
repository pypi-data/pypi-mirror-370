# UpdateRentalFile


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**product_id** | **str** |  | [optional] 
**meta** | **object** |  | [optional] 
**allow_user_engagement** | **bool** | If enabled, applicants will be able to access their data, and the system will allow email sending | [optional] [default to True]
**applicants_situation** | **str** |  | [optional] 
**applicants** | [**List[UpdateApplicant]**](UpdateApplicant.md) |  | [optional] [default to []]
**archived_at** | **datetime** |  | [optional] 

## Example

```python
from core.v2.models.update_rental_file import UpdateRentalFile

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateRentalFile from a JSON string
update_rental_file_instance = UpdateRentalFile.from_json(json)
# print the JSON string representation of the object
print(UpdateRentalFile.to_json())

# convert the object into a dict
update_rental_file_dict = update_rental_file_instance.to_dict()
# create an instance of UpdateRentalFile from a dict
update_rental_file_from_dict = UpdateRentalFile.from_dict(update_rental_file_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


