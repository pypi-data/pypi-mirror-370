# RentalFileStatus


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**status** | **str** |  | 

## Example

```python
from core.v2.models.rental_file_status import RentalFileStatus

# TODO update the JSON string below
json = "{}"
# create an instance of RentalFileStatus from a JSON string
rental_file_status_instance = RentalFileStatus.from_json(json)
# print the JSON string representation of the object
print(RentalFileStatus.to_json())

# convert the object into a dict
rental_file_status_dict = rental_file_status_instance.to_dict()
# create an instance of RentalFileStatus from a dict
rental_file_status_from_dict = RentalFileStatus.from_dict(rental_file_status_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


