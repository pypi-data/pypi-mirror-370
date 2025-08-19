# JsonParams


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**encoding** | **str** |  | [optional] 
**root_path** | **str** |  | [optional] [default to '']

## Example

```python
from products.v1.models.json_params import JsonParams

# TODO update the JSON string below
json = "{}"
# create an instance of JsonParams from a JSON string
json_params_instance = JsonParams.from_json(json)
# print the JSON string representation of the object
print(JsonParams.to_json())

# convert the object into a dict
json_params_dict = json_params_instance.to_dict()
# create an instance of JsonParams from a dict
json_params_from_dict = JsonParams.from_dict(json_params_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


