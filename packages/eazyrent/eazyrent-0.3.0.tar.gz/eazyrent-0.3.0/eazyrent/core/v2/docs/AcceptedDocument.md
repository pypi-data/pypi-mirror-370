# AcceptedDocument


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
**alerts_to_check** | **List[str]** |  | [optional] [default to []]

## Example

```python
from core.v2.models.accepted_document import AcceptedDocument

# TODO update the JSON string below
json = "{}"
# create an instance of AcceptedDocument from a JSON string
accepted_document_instance = AcceptedDocument.from_json(json)
# print the JSON string representation of the object
print(AcceptedDocument.to_json())

# convert the object into a dict
accepted_document_dict = accepted_document_instance.to_dict()
# create an instance of AcceptedDocument from a dict
accepted_document_from_dict = AcceptedDocument.from_dict(accepted_document_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


