# DocumentType


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**max_pages** | **int** |  | [optional] [default to 1]
**analyzed_as** | **str** |  | [optional] [default to 'NOT_ANALYZED']
**examples** | **List[str]** |  | [optional] [default to []]
**to_download** | [**ToDownload**](ToDownload.md) |  | [optional] 
**id** | **str** |  | [optional] 
**tenant** | **str** |  | 

## Example

```python
from core.v2.models.document_type import DocumentType

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentType from a JSON string
document_type_instance = DocumentType.from_json(json)
# print the JSON string representation of the object
print(DocumentType.to_json())

# convert the object into a dict
document_type_dict = document_type_instance.to_dict()
# create an instance of DocumentType from a dict
document_type_from_dict = DocumentType.from_dict(document_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


