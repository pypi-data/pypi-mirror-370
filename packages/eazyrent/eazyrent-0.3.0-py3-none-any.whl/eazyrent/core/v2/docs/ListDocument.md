# ListDocument


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**document_type** | [**DocumentType**](DocumentType.md) |  | [optional] 
**status** | **str** |  | [optional] [default to 'RECEIVED']
**created_at** | **datetime** |  | [optional] 
**updated_at** | **datetime** |  | [optional] 
**detected_model** | **str** |  | [optional] 
**alerts** | [**List[Alert]**](Alert.md) |  | [optional] [default to []]
**files** | [**List[DocumentSlice]**](DocumentSlice.md) |  | [optional] [default to []]

## Example

```python
from core.v2.models.list_document import ListDocument

# TODO update the JSON string below
json = "{}"
# create an instance of ListDocument from a JSON string
list_document_instance = ListDocument.from_json(json)
# print the JSON string representation of the object
print(ListDocument.to_json())

# convert the object into a dict
list_document_dict = list_document_instance.to_dict()
# create an instance of ListDocument from a dict
list_document_from_dict = ListDocument.from_dict(list_document_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


