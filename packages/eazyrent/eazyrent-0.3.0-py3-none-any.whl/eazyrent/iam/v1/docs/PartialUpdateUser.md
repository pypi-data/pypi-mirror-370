# PartialUpdateUser


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_type** | **str** |  | [optional] [default to 'Human']
**first_name** | **str** |  | [optional] 
**last_name** | **str** |  | [optional] 
**email** | **str** |  | [optional] 
**phone** | **str** |  | [optional] 

## Example

```python
from iam.v1.models.partial_update_user import PartialUpdateUser

# TODO update the JSON string below
json = "{}"
# create an instance of PartialUpdateUser from a JSON string
partial_update_user_instance = PartialUpdateUser.from_json(json)
# print the JSON string representation of the object
print(PartialUpdateUser.to_json())

# convert the object into a dict
partial_update_user_dict = partial_update_user_instance.to_dict()
# create an instance of PartialUpdateUser from a dict
partial_update_user_from_dict = PartialUpdateUser.from_dict(partial_update_user_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


