# PhotoColumn


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_field** | **str** |  | [optional] [default to 'photos']
**sub_field** | **str** |  | [optional] 
**suffix** | **str** |  | [optional] 

## Example

```python
from products.v1.models.photo_column import PhotoColumn

# TODO update the JSON string below
json = "{}"
# create an instance of PhotoColumn from a JSON string
photo_column_instance = PhotoColumn.from_json(json)
# print the JSON string representation of the object
print(PhotoColumn.to_json())

# convert the object into a dict
photo_column_dict = photo_column_instance.to_dict()
# create an instance of PhotoColumn from a dict
photo_column_from_dict = PhotoColumn.from_dict(photo_column_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


