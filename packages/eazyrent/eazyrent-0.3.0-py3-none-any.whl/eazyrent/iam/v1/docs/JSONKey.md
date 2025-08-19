# JSONKey


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**key_id** | **str** |  | 
**key** | **str** |  | 
**expiration_date** | **datetime** |  | 
**user_id** | **str** |  | 

## Example

```python
from iam.v1.models.json_key import JSONKey

# TODO update the JSON string below
json = "{}"
# create an instance of JSONKey from a JSON string
json_key_instance = JSONKey.from_json(json)
# print the JSON string representation of the object
print(JSONKey.to_json())

# convert the object into a dict
json_key_dict = json_key_instance.to_dict()
# create an instance of JSONKey from a dict
json_key_from_dict = JSONKey.from_dict(json_key_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


