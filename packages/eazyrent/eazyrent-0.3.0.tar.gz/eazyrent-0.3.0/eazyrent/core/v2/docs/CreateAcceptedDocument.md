# CreateAcceptedDocument


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
from core.v2.models.create_accepted_document import CreateAcceptedDocument

# TODO update the JSON string below
json = "{}"
# create an instance of CreateAcceptedDocument from a JSON string
create_accepted_document_instance = CreateAcceptedDocument.from_json(json)
# print the JSON string representation of the object
print(CreateAcceptedDocument.to_json())

# convert the object into a dict
create_accepted_document_dict = create_accepted_document_instance.to_dict()
# create an instance of CreateAcceptedDocument from a dict
create_accepted_document_from_dict = CreateAcceptedDocument.from_dict(create_accepted_document_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


