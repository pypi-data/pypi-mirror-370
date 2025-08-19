# ListServiceAccountKey


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**type** | **str** |  | 
**expiration_date** | **datetime** |  | 
**created_at** | **datetime** |  | 
**tenant** | **str** |  | 

## Example

```python
from iam.v1.models.list_service_account_key import ListServiceAccountKey

# TODO update the JSON string below
json = "{}"
# create an instance of ListServiceAccountKey from a JSON string
list_service_account_key_instance = ListServiceAccountKey.from_json(json)
# print the JSON string representation of the object
print(ListServiceAccountKey.to_json())

# convert the object into a dict
list_service_account_key_dict = list_service_account_key_instance.to_dict()
# create an instance of ListServiceAccountKey from a dict
list_service_account_key_from_dict = ListServiceAccountKey.from_dict(list_service_account_key_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


