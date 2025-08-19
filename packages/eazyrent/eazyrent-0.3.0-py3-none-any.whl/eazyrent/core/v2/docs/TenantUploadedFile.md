# TenantUploadedFile


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**number_of_pages** | **int** |  | [optional] 
**size** | **int** |  | [optional] 
**created_at** | **datetime** |  | [optional] 
**updated_at** | **datetime** |  | [optional] 
**status** | **str** |  | [optional] [default to 'RECEIVED']
**mime_type** | **str** |  | 
**uploaded_for_section** | **str** |  | [optional] 
**document_type** | **str** |  | [optional] 
**applicant** | **str** |  | 
**created_by** | **str** |  | [optional] 
**meta** | **object** |  | [optional] 
**reject_reason** | [**RejectReason**](RejectReason.md) |  | [optional] 
**id** | **str** |  | 

## Example

```python
from core.v2.models.tenant_uploaded_file import TenantUploadedFile

# TODO update the JSON string below
json = "{}"
# create an instance of TenantUploadedFile from a JSON string
tenant_uploaded_file_instance = TenantUploadedFile.from_json(json)
# print the JSON string representation of the object
print(TenantUploadedFile.to_json())

# convert the object into a dict
tenant_uploaded_file_dict = tenant_uploaded_file_instance.to_dict()
# create an instance of TenantUploadedFile from a dict
tenant_uploaded_file_from_dict = TenantUploadedFile.from_dict(tenant_uploaded_file_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


