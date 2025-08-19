# DocumentView


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**document_type** | **str** |  | [optional] 
**status** | **str** |  | [optional] [default to 'RECEIVED']
**created_at** | **datetime** |  | [optional] 
**updated_at** | **datetime** |  | [optional] 
**detected_model** | **str** |  | [optional] 
**alerts** | [**List[Alert]**](Alert.md) |  | [optional] [default to []]
**extraction_results** | **object** |  | [optional] 
**uploaded_for_section** | **str** |  | [optional] 
**files** | [**List[DocumentSlice]**](DocumentSlice.md) |  | [optional] [default to []]
**reject_reason** | [**RejectReason**](RejectReason.md) |  | [optional] 
**admin_attention_required** | **bool** |  | [optional] [default to False]
**tenant** | **str** |  | 
**applicant** | **str** |  | 
**document_info** | [**ListAcceptedDocument**](ListAcceptedDocument.md) |  | [optional] 

## Example

```python
from core.v2.models.document_view import DocumentView

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentView from a JSON string
document_view_instance = DocumentView.from_json(json)
# print the JSON string representation of the object
print(DocumentView.to_json())

# convert the object into a dict
document_view_dict = document_view_instance.to_dict()
# create an instance of DocumentView from a dict
document_view_from_dict = DocumentView.from_dict(document_view_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


