# Descriptor


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
from products.v1.models.descriptor import Descriptor

# TODO update the JSON string below
json = "{}"
# create an instance of Descriptor from a JSON string
descriptor_instance = Descriptor.from_json(json)
# print the JSON string representation of the object
print(Descriptor.to_json())

# convert the object into a dict
descriptor_dict = descriptor_instance.to_dict()
# create an instance of Descriptor from a dict
descriptor_from_dict = Descriptor.from_dict(descriptor_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


