# DocumentToUpload


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**max_pages** | **int** |  | [optional] [default to 1]
**analyzed_as** | **str** |  | [optional] [default to 'NOT_ANALYZED']
**examples** | **List[str]** |  | [optional] [default to []]
**to_download** | [**ToDownload**](ToDownload.md) |  | [optional] 
**id** | **str** |  | 

## Example

```python
from core.v2.models.document_to_upload import DocumentToUpload

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentToUpload from a JSON string
document_to_upload_instance = DocumentToUpload.from_json(json)
# print the JSON string representation of the object
print(DocumentToUpload.to_json())

# convert the object into a dict
document_to_upload_dict = document_to_upload_instance.to_dict()
# create an instance of DocumentToUpload from a dict
document_to_upload_from_dict = DocumentToUpload.from_dict(document_to_upload_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


