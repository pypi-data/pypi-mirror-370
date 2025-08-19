# ListUser


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

## Example

```python
from iam.v1.models.list_user import ListUser

# TODO update the JSON string below
json = "{}"
# create an instance of ListUser from a JSON string
list_user_instance = ListUser.from_json(json)
# print the JSON string representation of the object
print(ListUser.to_json())

# convert the object into a dict
list_user_dict = list_user_instance.to_dict()
# create an instance of ListUser from a dict
list_user_from_dict = ListUser.from_dict(list_user_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


