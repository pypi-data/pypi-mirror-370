# IdentityUserInfo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**identity** | [**Identity**](Identity.md) |  | 

## Example

```python
from core.v2.models.identity_user_info import IdentityUserInfo

# TODO update the JSON string below
json = "{}"
# create an instance of IdentityUserInfo from a JSON string
identity_user_info_instance = IdentityUserInfo.from_json(json)
# print the JSON string representation of the object
print(IdentityUserInfo.to_json())

# convert the object into a dict
identity_user_info_dict = identity_user_info_instance.to_dict()
# create an instance of IdentityUserInfo from a dict
identity_user_info_from_dict = IdentityUserInfo.from_dict(identity_user_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


