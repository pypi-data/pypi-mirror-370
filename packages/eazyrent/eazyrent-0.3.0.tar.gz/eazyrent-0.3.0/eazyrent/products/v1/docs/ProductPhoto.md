# ProductPhoto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**size** | **int** |  | 
**path** | **str** |  | [optional] 
**filename** | **str** |  | 
**content_type** | **str** |  | 
**favorite** | **bool** |  | [optional] [default to False]

## Example

```python
from products.v1.models.product_photo import ProductPhoto

# TODO update the JSON string below
json = "{}"
# create an instance of ProductPhoto from a JSON string
product_photo_instance = ProductPhoto.from_json(json)
# print the JSON string representation of the object
print(ProductPhoto.to_json())

# convert the object into a dict
product_photo_dict = product_photo_instance.to_dict()
# create an instance of ProductPhoto from a dict
product_photo_from_dict = ProductPhoto.from_dict(product_photo_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


