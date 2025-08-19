# PaginatedResponseRentalFileFull


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** |  | [optional] [default to 0]
**next** | [**Next**](Next.md) |  | [optional] 
**previous** | [**Previous**](Previous.md) |  | [optional] 
**results** | [**List[RentalFileFull]**](RentalFileFull.md) |  | [optional] [default to []]

## Example

```python
from core.v1.models.paginated_response_rental_file_full import PaginatedResponseRentalFileFull

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResponseRentalFileFull from a JSON string
paginated_response_rental_file_full_instance = PaginatedResponseRentalFileFull.from_json(json)
# print the JSON string representation of the object
print(PaginatedResponseRentalFileFull.to_json())

# convert the object into a dict
paginated_response_rental_file_full_dict = paginated_response_rental_file_full_instance.to_dict()
# create an instance of PaginatedResponseRentalFileFull from a dict
paginated_response_rental_file_full_from_dict = PaginatedResponseRentalFileFull.from_dict(paginated_response_rental_file_full_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


