# ListAcceptedDocument


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
from core.v2.models.list_accepted_document import ListAcceptedDocument

# TODO update the JSON string below
json = "{}"
# create an instance of ListAcceptedDocument from a JSON string
list_accepted_document_instance = ListAcceptedDocument.from_json(json)
# print the JSON string representation of the object
print(ListAcceptedDocument.to_json())

# convert the object into a dict
list_accepted_document_dict = list_accepted_document_instance.to_dict()
# create an instance of ListAcceptedDocument from a dict
list_accepted_document_from_dict = ListAcceptedDocument.from_dict(list_accepted_document_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


