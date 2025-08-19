# RegisterSerializer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**organization** | [**RegisterOrganizationSerializer**](RegisterOrganizationSerializer.md) |  | 
**org_admin** | [**RegisterAdminOrgSerializer**](RegisterAdminOrgSerializer.md) |  | 

## Example

```python
from iam.v1.models.register_serializer import RegisterSerializer

# TODO update the JSON string below
json = "{}"
# create an instance of RegisterSerializer from a JSON string
register_serializer_instance = RegisterSerializer.from_json(json)
# print the JSON string representation of the object
print(RegisterSerializer.to_json())

# convert the object into a dict
register_serializer_dict = register_serializer_instance.to_dict()
# create an instance of RegisterSerializer from a dict
register_serializer_from_dict = RegisterSerializer.from_dict(register_serializer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


