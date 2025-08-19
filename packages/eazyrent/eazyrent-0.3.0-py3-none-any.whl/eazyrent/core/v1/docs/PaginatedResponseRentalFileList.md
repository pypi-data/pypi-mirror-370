# PaginatedResponseRentalFileList


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** |  | [optional] [default to 0]
**next** | [**Next**](Next.md) |  | [optional] 
**previous** | [**Previous**](Previous.md) |  | [optional] 
**results** | [**List[RentalFileList]**](RentalFileList.md) |  | [optional] [default to []]

## Example

```python
from core.v1.models.paginated_response_rental_file_list import PaginatedResponseRentalFileList

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResponseRentalFileList from a JSON string
paginated_response_rental_file_list_instance = PaginatedResponseRentalFileList.from_json(json)
# print the JSON string representation of the object
print(PaginatedResponseRentalFileList.to_json())

# convert the object into a dict
paginated_response_rental_file_list_dict = paginated_response_rental_file_list_instance.to_dict()
# create an instance of PaginatedResponseRentalFileList from a dict
paginated_response_rental_file_list_from_dict = PaginatedResponseRentalFileList.from_dict(paginated_response_rental_file_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


