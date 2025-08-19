# XmlDescriptor


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
**xml_params** | [**XmlParams**](XmlParams.md) |  | 

## Example

```python
from products.v1.models.xml_descriptor import XmlDescriptor

# TODO update the JSON string below
json = "{}"
# create an instance of XmlDescriptor from a JSON string
xml_descriptor_instance = XmlDescriptor.from_json(json)
# print the JSON string representation of the object
print(XmlDescriptor.to_json())

# convert the object into a dict
xml_descriptor_dict = xml_descriptor_instance.to_dict()
# create an instance of XmlDescriptor from a dict
xml_descriptor_from_dict = XmlDescriptor.from_dict(xml_descriptor_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


