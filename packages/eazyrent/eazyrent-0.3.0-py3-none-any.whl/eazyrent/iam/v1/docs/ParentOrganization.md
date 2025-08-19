# ParentOrganization


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**name** | **str** |  | 
**logo** | [**Logo**](Logo.md) |  | [optional] 

## Example

```python
from iam.v1.models.parent_organization import ParentOrganization

# TODO update the JSON string below
json = "{}"
# create an instance of ParentOrganization from a JSON string
parent_organization_instance = ParentOrganization.from_json(json)
# print the JSON string representation of the object
print(ParentOrganization.to_json())

# convert the object into a dict
parent_organization_dict = parent_organization_instance.to_dict()
# create an instance of ParentOrganization from a dict
parent_organization_from_dict = ParentOrganization.from_dict(parent_organization_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


