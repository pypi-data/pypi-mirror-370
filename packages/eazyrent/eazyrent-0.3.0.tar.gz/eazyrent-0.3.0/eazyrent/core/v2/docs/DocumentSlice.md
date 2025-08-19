# DocumentSlice


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**file_id** | **str** |  | 
**file** | [**File**](File.md) |  | 
**thumbnail** | [**Thumbnail**](Thumbnail.md) |  | 
**images** | [**Images**](Images.md) |  | 
**pages** | **List[int]** |  | [optional] [default to []]

## Example

```python
from core.v2.models.document_slice import DocumentSlice

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentSlice from a JSON string
document_slice_instance = DocumentSlice.from_json(json)
# print the JSON string representation of the object
print(DocumentSlice.to_json())

# convert the object into a dict
document_slice_dict = document_slice_instance.to_dict()
# create an instance of DocumentSlice from a dict
document_slice_from_dict = DocumentSlice.from_dict(document_slice_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


