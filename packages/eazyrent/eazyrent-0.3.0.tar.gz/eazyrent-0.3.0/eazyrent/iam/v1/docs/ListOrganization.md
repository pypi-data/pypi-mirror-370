# ListOrganization


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**organization_id** | **str** |  | [optional] 
**insurance_id** | **str** |  | [optional] 
**logo** | [**Logo**](Logo.md) |  | [optional] 
**registration_number** | **str** |  | [optional] 
**address** | **str** |  | [optional] 
**account_type** | **str** |  | [optional] [default to 'DEFAULT']
**id** | **str** |  | 

## Example

```python
from iam.v1.models.list_organization import ListOrganization

# TODO update the JSON string below
json = "{}"
# create an instance of ListOrganization from a JSON string
list_organization_instance = ListOrganization.from_json(json)
# print the JSON string representation of the object
print(ListOrganization.to_json())

# convert the object into a dict
list_organization_dict = list_organization_instance.to_dict()
# create an instance of ListOrganization from a dict
list_organization_from_dict = ListOrganization.from_dict(list_organization_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


