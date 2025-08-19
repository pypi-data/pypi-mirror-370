# ComputedColumn


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**mode** | **str** |  | 
**fields** | **List[str]** |  | 
**separator** | **str** |  | [optional] 
**regex** | **str** |  | [optional] 

## Example

```python
from products.v1.models.computed_column import ComputedColumn

# TODO update the JSON string below
json = "{}"
# create an instance of ComputedColumn from a JSON string
computed_column_instance = ComputedColumn.from_json(json)
# print the JSON string representation of the object
print(ComputedColumn.to_json())

# convert the object into a dict
computed_column_dict = computed_column_instance.to_dict()
# create an instance of ComputedColumn from a dict
computed_column_from_dict = ComputedColumn.from_dict(computed_column_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


