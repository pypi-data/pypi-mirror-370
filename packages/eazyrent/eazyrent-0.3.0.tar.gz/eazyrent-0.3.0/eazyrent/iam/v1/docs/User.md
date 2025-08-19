# User


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_type** | **str** |  | [optional] [default to 'Human']
**first_name** | **str** |  | [optional] 
**last_name** | **str** |  | [optional] 
**email** | **str** |  | [optional] 
**phone** | **str** |  | [optional] 
**id** | **str** |  | 
**avatar** | **str** |  | [optional] 
**state** | **str** |  | [optional] [default to 'USER_STATE_UNSPECIFIED']
**config** | [**UserConfig**](UserConfig.md) |  | [optional] 
**organization** | [**ListOrganization**](ListOrganization.md) |  | [optional] 
**updated_at** | **datetime** |  | [optional] 

## Example

```python
from iam.v1.models.user import User

# TODO update the JSON string below
json = "{}"
# create an instance of User from a JSON string
user_instance = User.from_json(json)
# print the JSON string representation of the object
print(User.to_json())

# convert the object into a dict
user_dict = user_instance.to_dict()
# create an instance of User from a dict
user_from_dict = User.from_dict(user_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


