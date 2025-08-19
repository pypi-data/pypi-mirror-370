# PartialUpdateRentalFile

Schema for PATCH /v2/rental-files/:id

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**product_id** | **str** |  | [optional] 
**meta** | **object** |  | [optional] 
**allow_user_engagement** | **bool** | If enabled, applicants will be able to access their data, and the system will allow email sending | [optional] [default to True]
**archived_at** | **datetime** |  | [optional] 
**tags** | [**List[TagIn]**](TagIn.md) |  | [optional] 
**managers** | **List[str]** |  | [optional] 
**applicants_situation** | **str** |  | [optional] 
**decision** | **str** |  | [optional] 

## Example

```python
from core.v2.models.partial_update_rental_file import PartialUpdateRentalFile

# TODO update the JSON string below
json = "{}"
# create an instance of PartialUpdateRentalFile from a JSON string
partial_update_rental_file_instance = PartialUpdateRentalFile.from_json(json)
# print the JSON string representation of the object
print(PartialUpdateRentalFile.to_json())

# convert the object into a dict
partial_update_rental_file_dict = partial_update_rental_file_instance.to_dict()
# create an instance of PartialUpdateRentalFile from a dict
partial_update_rental_file_from_dict = PartialUpdateRentalFile.from_dict(partial_update_rental_file_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


