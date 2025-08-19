# ZipParams


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**file_path** | **str** |  | 
**descriptor** | [**Descriptor**](Descriptor.md) |  | 

## Example

```python
from products.v1.models.zip_params import ZipParams

# TODO update the JSON string below
json = "{}"
# create an instance of ZipParams from a JSON string
zip_params_instance = ZipParams.from_json(json)
# print the JSON string representation of the object
print(ZipParams.to_json())

# convert the object into a dict
zip_params_dict = zip_params_instance.to_dict()
# create an instance of ZipParams from a dict
zip_params_from_dict = ZipParams.from_dict(zip_params_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


