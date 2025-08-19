# JsonDescriptor


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**match_on** | **List[str]** |  | 
**columns** | **Dict[str, str]** |  | 
**computed_columns** | [**Dict[str, ComputedColumn]**](ComputedColumn.md) |  | [optional] 
**type_casts** | **Dict[str, str]** |  | [optional] 
**defaults** | **Dict[str, str]** |  | [optional] 
**photos** | [**PhotoColumn**](PhotoColumn.md) |  | [optional] 
**format** | **str** |  | 
**json_params** | [**JsonParams**](JsonParams.md) |  | 

## Example

```python
from products.v1.models.json_descriptor import JsonDescriptor

# TODO update the JSON string below
json = "{}"
# create an instance of JsonDescriptor from a JSON string
json_descriptor_instance = JsonDescriptor.from_json(json)
# print the JSON string representation of the object
print(JsonDescriptor.to_json())

# convert the object into a dict
json_descriptor_dict = json_descriptor_instance.to_dict()
# create an instance of JsonDescriptor from a dict
json_descriptor_from_dict = JsonDescriptor.from_dict(json_descriptor_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


