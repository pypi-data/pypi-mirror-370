# LightUploadFile


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**format** | [**FormatEnum**](FormatEnum.md) |  | 
**number_of_pages** | **int** |  | 
**file** | **str** |  | 

## Example

```python
from core.v1.models.light_upload_file import LightUploadFile

# TODO update the JSON string below
json = "{}"
# create an instance of LightUploadFile from a JSON string
light_upload_file_instance = LightUploadFile.from_json(json)
# print the JSON string representation of the object
print(LightUploadFile.to_json())

# convert the object into a dict
light_upload_file_dict = light_upload_file_instance.to_dict()
# create an instance of LightUploadFile from a dict
light_upload_file_from_dict = LightUploadFile.from_dict(light_upload_file_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


