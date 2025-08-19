# CreateOrganization


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

## Example

```python
from iam.v1.models.create_organization import CreateOrganization

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOrganization from a JSON string
create_organization_instance = CreateOrganization.from_json(json)
# print the JSON string representation of the object
print(CreateOrganization.to_json())

# convert the object into a dict
create_organization_dict = create_organization_instance.to_dict()
# create an instance of CreateOrganization from a dict
create_organization_from_dict = CreateOrganization.from_dict(create_organization_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


