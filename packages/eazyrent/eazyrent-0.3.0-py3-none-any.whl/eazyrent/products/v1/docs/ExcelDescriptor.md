# ExcelDescriptor


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
**excel_params** | [**ExcelParams**](ExcelParams.md) |  | 

## Example

```python
from products.v1.models.excel_descriptor import ExcelDescriptor

# TODO update the JSON string below
json = "{}"
# create an instance of ExcelDescriptor from a JSON string
excel_descriptor_instance = ExcelDescriptor.from_json(json)
# print the JSON string representation of the object
print(ExcelDescriptor.to_json())

# convert the object into a dict
excel_descriptor_dict = excel_descriptor_instance.to_dict()
# create an instance of ExcelDescriptor from a dict
excel_descriptor_from_dict = ExcelDescriptor.from_dict(excel_descriptor_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


