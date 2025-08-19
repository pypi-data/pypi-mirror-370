# PropertyRentList


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**reference** | **str** |  | [optional] 
**photo_uri** | **str** |  | [optional] 
**title** | **str** |  | 
**rent_amount** | **float** |  | 
**added_at** | **datetime** |  | 
**applicant_file_count** | **int** |  | [optional] [default to 0]

## Example

```python
from core.v1.models.property_rent_list import PropertyRentList

# TODO update the JSON string below
json = "{}"
# create an instance of PropertyRentList from a JSON string
property_rent_list_instance = PropertyRentList.from_json(json)
# print the JSON string representation of the object
print(PropertyRentList.to_json())

# convert the object into a dict
property_rent_list_dict = property_rent_list_instance.to_dict()
# create an instance of PropertyRentList from a dict
property_rent_list_from_dict = PropertyRentList.from_dict(property_rent_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


