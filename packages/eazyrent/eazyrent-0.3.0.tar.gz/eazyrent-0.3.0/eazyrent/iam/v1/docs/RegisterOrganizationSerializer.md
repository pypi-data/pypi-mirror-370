# RegisterOrganizationSerializer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**registration_number** | **str** |  | 
**pairing_code** | **str** |  | [optional] 

## Example

```python
from iam.v1.models.register_organization_serializer import RegisterOrganizationSerializer

# TODO update the JSON string below
json = "{}"
# create an instance of RegisterOrganizationSerializer from a JSON string
register_organization_serializer_instance = RegisterOrganizationSerializer.from_json(json)
# print the JSON string representation of the object
print(RegisterOrganizationSerializer.to_json())

# convert the object into a dict
register_organization_serializer_dict = register_organization_serializer_instance.to_dict()
# create an instance of RegisterOrganizationSerializer from a dict
register_organization_serializer_from_dict = RegisterOrganizationSerializer.from_dict(register_organization_serializer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


