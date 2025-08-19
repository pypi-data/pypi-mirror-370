# TenantForm

This document is used to reflect the progress in the document collect

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**parts** | [**List[FormPart]**](FormPart.md) |  | [optional] [default to []]
**comment** | **str** |  | [optional] 

## Example

```python
from core.v2.models.tenant_form import TenantForm

# TODO update the JSON string below
json = "{}"
# create an instance of TenantForm from a JSON string
tenant_form_instance = TenantForm.from_json(json)
# print the JSON string representation of the object
print(TenantForm.to_json())

# convert the object into a dict
tenant_form_dict = tenant_form_instance.to_dict()
# create an instance of TenantForm from a dict
tenant_form_from_dict = TenantForm.from_dict(tenant_form_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


