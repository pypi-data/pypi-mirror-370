# UpdateAcceptedDocument


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**max_pages** | **int** |  | [optional] [default to 1]
**analyzed_as** | **str** |  | [optional] [default to 'NOT_ANALYZED']
**examples** | **List[str]** |  | [optional] [default to []]
**to_download** | [**ToDownload**](ToDownload.md) |  | [optional] 
**alerts_to_check** | **List[str]** |  | [optional] [default to []]

## Example

```python
from core.v2.models.update_accepted_document import UpdateAcceptedDocument

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateAcceptedDocument from a JSON string
update_accepted_document_instance = UpdateAcceptedDocument.from_json(json)
# print the JSON string representation of the object
print(UpdateAcceptedDocument.to_json())

# convert the object into a dict
update_accepted_document_dict = update_accepted_document_instance.to_dict()
# create an instance of UpdateAcceptedDocument from a dict
update_accepted_document_from_dict = UpdateAcceptedDocument.from_dict(update_accepted_document_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


