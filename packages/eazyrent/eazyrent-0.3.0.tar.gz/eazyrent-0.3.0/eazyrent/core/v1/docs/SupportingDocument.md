# SupportingDocument


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**uploaded_files** | [**List[LightUploadFile]**](LightUploadFile.md) |  | [optional] [default to []]
**alerts** | [**List[AlertPretty]**](AlertPretty.md) |  | [optional] [default to []]
**applicant** | **str** |  | 
**document_type** | **str** |  | [optional] 
**status** | [**Status6d0Enum**](Status6d0Enum.md) |  | 
**document_type_name** | **str** |  | [optional] 
**created_at** | **datetime** |  | 
**size** | **int** |  | [optional] [default to 0]
**reject_reason** | [**RejectReasonEnum**](RejectReasonEnum.md) |  | [optional] 
**uploaded_for_section** | **str** |  | [optional] 

## Example

```python
from core.v1.models.supporting_document import SupportingDocument

# TODO update the JSON string below
json = "{}"
# create an instance of SupportingDocument from a JSON string
supporting_document_instance = SupportingDocument.from_json(json)
# print the JSON string representation of the object
print(SupportingDocument.to_json())

# convert the object into a dict
supporting_document_dict = supporting_document_instance.to_dict()
# create an instance of SupportingDocument from a dict
supporting_document_from_dict = SupportingDocument.from_dict(supporting_document_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


