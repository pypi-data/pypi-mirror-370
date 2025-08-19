# CreateRentalFile

Schema for POST /v2/rental-files.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**product_id** | **str** |  | [optional] 
**meta** | **object** |  | [optional] 
**allow_user_engagement** | **bool** | If enabled, applicants will be able to access their data, and the system will allow email sending | [optional] [default to True]
**applicants_situation** | **str** |  | [optional] 
**applicants** | [**List[CreateApplicant]**](CreateApplicant.md) |  | [optional] [default to []]

## Example

```python
from core.v2.models.create_rental_file import CreateRentalFile

# TODO update the JSON string below
json = "{}"
# create an instance of CreateRentalFile from a JSON string
create_rental_file_instance = CreateRentalFile.from_json(json)
# print the JSON string representation of the object
print(CreateRentalFile.to_json())

# convert the object into a dict
create_rental_file_dict = create_rental_file_instance.to_dict()
# create an instance of CreateRentalFile from a dict
create_rental_file_from_dict = CreateRentalFile.from_dict(create_rental_file_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


