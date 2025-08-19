# SupportingDocumentList


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**document_type** | **str** |  | [optional] 
**document_name** | **str** |  | [optional] 
**applicant** | **str** |  | 
**status** | [**Status6d0Enum**](Status6d0Enum.md) |  | 
**reject_reason** | [**RejectReasonEnum**](RejectReasonEnum.md) |  | [optional] 
**uploaded_for_section** | **str** |  | [optional] 

## Example

```python
from core.v1.models.supporting_document_list import SupportingDocumentList

# TODO update the JSON string below
json = "{}"
# create an instance of SupportingDocumentList from a JSON string
supporting_document_list_instance = SupportingDocumentList.from_json(json)
# print the JSON string representation of the object
print(SupportingDocumentList.to_json())

# convert the object into a dict
supporting_document_list_dict = supporting_document_list_instance.to_dict()
# create an instance of SupportingDocumentList from a dict
supporting_document_list_from_dict = SupportingDocumentList.from_dict(supporting_document_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


