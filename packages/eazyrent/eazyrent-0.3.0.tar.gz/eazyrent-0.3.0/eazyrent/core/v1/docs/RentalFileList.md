# RentalFileList


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**status** | [**StatusD7bEnum**](StatusD7bEnum.md) |  | [optional] 
**property_rent** | **str** |  | 
**applicants** | **List[str]** |  | 

## Example

```python
from core.v1.models.rental_file_list import RentalFileList

# TODO update the JSON string below
json = "{}"
# create an instance of RentalFileList from a JSON string
rental_file_list_instance = RentalFileList.from_json(json)
# print the JSON string representation of the object
print(RentalFileList.to_json())

# convert the object into a dict
rental_file_list_dict = rental_file_list_instance.to_dict()
# create an instance of RentalFileList from a dict
rental_file_list_from_dict = RentalFileList.from_dict(rental_file_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


