# PaginatedResponseListRentalFile


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** |  | [optional] [default to 0]
**next** | [**Next**](Next.md) |  | [optional] 
**previous** | [**Previous**](Previous.md) |  | [optional] 
**results** | [**List[ListRentalFile]**](ListRentalFile.md) |  | [optional] [default to []]

## Example

```python
from core.v2.models.paginated_response_list_rental_file import PaginatedResponseListRentalFile

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResponseListRentalFile from a JSON string
paginated_response_list_rental_file_instance = PaginatedResponseListRentalFile.from_json(json)
# print the JSON string representation of the object
print(PaginatedResponseListRentalFile.to_json())

# convert the object into a dict
paginated_response_list_rental_file_dict = paginated_response_list_rental_file_instance.to_dict()
# create an instance of PaginatedResponseListRentalFile from a dict
paginated_response_list_rental_file_from_dict = PaginatedResponseListRentalFile.from_dict(paginated_response_list_rental_file_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


