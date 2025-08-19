# RegisterAdminOrgSerializer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**first_name** | **str** |  | 
**last_name** | **str** |  | 
**email** | **str** |  | 
**phone** | **str** |  | [optional] 

## Example

```python
from iam.v1.models.register_admin_org_serializer import RegisterAdminOrgSerializer

# TODO update the JSON string below
json = "{}"
# create an instance of RegisterAdminOrgSerializer from a JSON string
register_admin_org_serializer_instance = RegisterAdminOrgSerializer.from_json(json)
# print the JSON string representation of the object
print(RegisterAdminOrgSerializer.to_json())

# convert the object into a dict
register_admin_org_serializer_dict = register_admin_org_serializer_instance.to_dict()
# create an instance of RegisterAdminOrgSerializer from a dict
register_admin_org_serializer_from_dict = RegisterAdminOrgSerializer.from_dict(register_admin_org_serializer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


