# DocumentSection


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**title** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**component** | **str** |  | [optional] [default to 'DocumentCollectSection']
**mandatory** | **bool** |  | [optional] [default to False]
**display_condition** | [**DisplayCondition**](DisplayCondition.md) |  | [optional] 
**documents** | [**List[DocumentToUpload]**](DocumentToUpload.md) |  | [optional] [default to []]
**min_docs** | **int** |  | [optional] [default to 1]
**completed** | **bool** |  | [optional] [default to False]
**uploads** | [**List[TenantUploadedFile]**](TenantUploadedFile.md) |  | [optional] [default to []]
**display** | **bool** |  | [optional] [default to True]

## Example

```python
from core.v2.models.document_section import DocumentSection

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentSection from a JSON string
document_section_instance = DocumentSection.from_json(json)
# print the JSON string representation of the object
print(DocumentSection.to_json())

# convert the object into a dict
document_section_dict = document_section_instance.to_dict()
# create an instance of DocumentSection from a dict
document_section_from_dict = DocumentSection.from_dict(document_section_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


