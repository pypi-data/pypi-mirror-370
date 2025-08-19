# PartialUpdateAcceptedDocument


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**max_pages** | **int** |  | [optional] 
**analyzed_as** | **str** |  | [optional] 
**examples** | **List[str]** |  | [optional] [default to []]
**to_download** | [**ToDownload**](ToDownload.md) |  | [optional] 

## Example

```python
from core.v2.models.partial_update_accepted_document import PartialUpdateAcceptedDocument

# TODO update the JSON string below
json = "{}"
# create an instance of PartialUpdateAcceptedDocument from a JSON string
partial_update_accepted_document_instance = PartialUpdateAcceptedDocument.from_json(json)
# print the JSON string representation of the object
print(PartialUpdateAcceptedDocument.to_json())

# convert the object into a dict
partial_update_accepted_document_dict = partial_update_accepted_document_instance.to_dict()
# create an instance of PartialUpdateAcceptedDocument from a dict
partial_update_accepted_document_from_dict = PartialUpdateAcceptedDocument.from_dict(partial_update_accepted_document_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


