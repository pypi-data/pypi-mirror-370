# ResponseGetMyUser


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_type** | **str** |  | [optional] [default to 'Machine']
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
**name** | **str** |  | [optional] 

## Example

```python
from iam.v1.models.response_get_my_user import ResponseGetMyUser

# TODO update the JSON string below
json = "{}"
# create an instance of ResponseGetMyUser from a JSON string
response_get_my_user_instance = ResponseGetMyUser.from_json(json)
# print the JSON string representation of the object
print(ResponseGetMyUser.to_json())

# convert the object into a dict
response_get_my_user_dict = response_get_my_user_instance.to_dict()
# create an instance of ResponseGetMyUser from a dict
response_get_my_user_from_dict = ResponseGetMyUser.from_dict(response_get_my_user_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


