# XmlParams


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**encoding** | **str** |  | [optional] 
**root_path** | **str** |  | [optional] [default to '']

## Example

```python
from products.v1.models.xml_params import XmlParams

# TODO update the JSON string below
json = "{}"
# create an instance of XmlParams from a JSON string
xml_params_instance = XmlParams.from_json(json)
# print the JSON string representation of the object
print(XmlParams.to_json())

# convert the object into a dict
xml_params_dict = xml_params_instance.to_dict()
# create an instance of XmlParams from a dict
xml_params_from_dict = XmlParams.from_dict(xml_params_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


