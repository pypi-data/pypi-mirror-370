# CsvParams


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**delimiter** | **str** |  | [optional] 
**encoding** | **str** |  | [optional] 
**skip_rows** | **int** |  | [optional] 

## Example

```python
from products.v1.models.csv_params import CsvParams

# TODO update the JSON string below
json = "{}"
# create an instance of CsvParams from a JSON string
csv_params_instance = CsvParams.from_json(json)
# print the JSON string representation of the object
print(CsvParams.to_json())

# convert the object into a dict
csv_params_dict = csv_params_instance.to_dict()
# create an instance of CsvParams from a dict
csv_params_from_dict = CsvParams.from_dict(csv_params_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


