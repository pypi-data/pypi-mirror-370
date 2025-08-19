# ExcelParams


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sheet_name** | [**SheetName**](SheetName.md) |  | [optional] 
**skiprows** | **int** |  | [optional] 
**header** | **int** |  | [optional] 
**usecols** | [**Usecols**](Usecols.md) |  | [optional] 
**skipfooter** | **int** |  | [optional] 
**dtype** | **Dict[str, object]** |  | [optional] 
**na_values** | **List[str]** |  | [optional] 

## Example

```python
from products.v1.models.excel_params import ExcelParams

# TODO update the JSON string below
json = "{}"
# create an instance of ExcelParams from a JSON string
excel_params_instance = ExcelParams.from_json(json)
# print the JSON string representation of the object
print(ExcelParams.to_json())

# convert the object into a dict
excel_params_dict = excel_params_instance.to_dict()
# create an instance of ExcelParams from a dict
excel_params_from_dict = ExcelParams.from_dict(excel_params_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


