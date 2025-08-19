# ZipDescriptor


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**format** | **str** |  | 
**zip_params** | [**ZipParams**](ZipParams.md) |  | 

## Example

```python
from products.v1.models.zip_descriptor import ZipDescriptor

# TODO update the JSON string below
json = "{}"
# create an instance of ZipDescriptor from a JSON string
zip_descriptor_instance = ZipDescriptor.from_json(json)
# print the JSON string representation of the object
print(ZipDescriptor.to_json())

# convert the object into a dict
zip_descriptor_dict = zip_descriptor_instance.to_dict()
# create an instance of ZipDescriptor from a dict
zip_descriptor_from_dict = ZipDescriptor.from_dict(zip_descriptor_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


