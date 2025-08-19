# PaginatedResponsePropertyRentList


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** |  | [optional] [default to 0]
**next** | [**Next**](Next.md) |  | [optional] 
**previous** | [**Previous**](Previous.md) |  | [optional] 
**results** | [**List[PropertyRentList]**](PropertyRentList.md) |  | [optional] [default to []]

## Example

```python
from core.v1.models.paginated_response_property_rent_list import PaginatedResponsePropertyRentList

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResponsePropertyRentList from a JSON string
paginated_response_property_rent_list_instance = PaginatedResponsePropertyRentList.from_json(json)
# print the JSON string representation of the object
print(PaginatedResponsePropertyRentList.to_json())

# convert the object into a dict
paginated_response_property_rent_list_dict = paginated_response_property_rent_list_instance.to_dict()
# create an instance of PaginatedResponsePropertyRentList from a dict
paginated_response_property_rent_list_from_dict = PaginatedResponsePropertyRentList.from_dict(paginated_response_property_rent_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


