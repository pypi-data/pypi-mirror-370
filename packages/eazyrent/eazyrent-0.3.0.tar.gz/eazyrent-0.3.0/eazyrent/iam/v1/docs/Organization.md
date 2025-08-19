# Organization


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
**id** | **str** |  | [optional] 
**organization** | [**ParentOrganization**](ParentOrganization.md) |  | [optional] 
**insurance** | [**ParentOrganization**](ParentOrganization.md) |  | [optional] 

## Example

```python
from iam.v1.models.organization import Organization

# TODO update the JSON string below
json = "{}"
# create an instance of Organization from a JSON string
organization_instance = Organization.from_json(json)
# print the JSON string representation of the object
print(Organization.to_json())

# convert the object into a dict
organization_dict = organization_instance.to_dict()
# create an instance of Organization from a dict
organization_from_dict = Organization.from_dict(organization_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


