# JoinOrganization


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**pairing_code** | **str** |  | 

## Example

```python
from iam.v1.models.join_organization import JoinOrganization

# TODO update the JSON string below
json = "{}"
# create an instance of JoinOrganization from a JSON string
join_organization_instance = JoinOrganization.from_json(json)
# print the JSON string representation of the object
print(JoinOrganization.to_json())

# convert the object into a dict
join_organization_dict = join_organization_instance.to_dict()
# create an instance of JoinOrganization from a dict
join_organization_from_dict = JoinOrganization.from_dict(join_organization_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


