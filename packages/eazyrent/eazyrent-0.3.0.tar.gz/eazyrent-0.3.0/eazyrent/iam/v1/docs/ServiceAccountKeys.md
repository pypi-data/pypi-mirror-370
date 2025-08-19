# ServiceAccountKeys


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** |  | [optional] [default to 0]
**results** | [**List[ListServiceAccountKey]**](ListServiceAccountKey.md) |  | [optional] [default to []]

## Example

```python
from iam.v1.models.service_account_keys import ServiceAccountKeys

# TODO update the JSON string below
json = "{}"
# create an instance of ServiceAccountKeys from a JSON string
service_account_keys_instance = ServiceAccountKeys.from_json(json)
# print the JSON string representation of the object
print(ServiceAccountKeys.to_json())

# convert the object into a dict
service_account_keys_dict = service_account_keys_instance.to_dict()
# create an instance of ServiceAccountKeys from a dict
service_account_keys_from_dict = ServiceAccountKeys.from_dict(service_account_keys_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


