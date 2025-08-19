# CsvDescriptor


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
**csv_params** | [**CsvParams**](CsvParams.md) |  | 

## Example

```python
from products.v1.models.csv_descriptor import CsvDescriptor

# TODO update the JSON string below
json = "{}"
# create an instance of CsvDescriptor from a JSON string
csv_descriptor_instance = CsvDescriptor.from_json(json)
# print the JSON string representation of the object
print(CsvDescriptor.to_json())

# convert the object into a dict
csv_descriptor_dict = csv_descriptor_instance.to_dict()
# create an instance of CsvDescriptor from a dict
csv_descriptor_from_dict = CsvDescriptor.from_dict(csv_descriptor_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


