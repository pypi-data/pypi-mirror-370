# UpdateUserGrants


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**grants** | [**List[UpdateUserGrantsGrantsInner]**](UpdateUserGrantsGrantsInner.md) |  | [optional] [default to []]

## Example

```python
from iam.v1.models.update_user_grants import UpdateUserGrants

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateUserGrants from a JSON string
update_user_grants_instance = UpdateUserGrants.from_json(json)
# print the JSON string representation of the object
print(UpdateUserGrants.to_json())

# convert the object into a dict
update_user_grants_dict = update_user_grants_instance.to_dict()
# create an instance of UpdateUserGrants from a dict
update_user_grants_from_dict = UpdateUserGrants.from_dict(update_user_grants_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


