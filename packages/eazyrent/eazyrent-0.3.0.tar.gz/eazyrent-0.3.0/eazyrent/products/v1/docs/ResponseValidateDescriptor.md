# ResponseValidateDescriptor


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
**json_params** | [**JsonParams**](JsonParams.md) |  | 
**xml_params** | [**XmlParams**](XmlParams.md) |  | 
**zip_params** | [**ZipParams**](ZipParams.md) |  | 
**excel_params** | [**ExcelParams**](ExcelParams.md) |  | 

## Example

```python
from products.v1.models.response_validate_descriptor import ResponseValidateDescriptor

# TODO update the JSON string below
json = "{}"
# create an instance of ResponseValidateDescriptor from a JSON string
response_validate_descriptor_instance = ResponseValidateDescriptor.from_json(json)
# print the JSON string representation of the object
print(ResponseValidateDescriptor.to_json())

# convert the object into a dict
response_validate_descriptor_dict = response_validate_descriptor_instance.to_dict()
# create an instance of ResponseValidateDescriptor from a dict
response_validate_descriptor_from_dict = ResponseValidateDescriptor.from_dict(response_validate_descriptor_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


