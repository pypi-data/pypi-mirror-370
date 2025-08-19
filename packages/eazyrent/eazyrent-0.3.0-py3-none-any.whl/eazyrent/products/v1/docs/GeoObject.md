# GeoObject


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | [optional] [default to 'Point']
**coordinates** | **List[object]** |  | 
**format** | **str** |  | [optional] [default to 'EPSG:2154']

## Example

```python
from products.v1.models.geo_object import GeoObject

# TODO update the JSON string below
json = "{}"
# create an instance of GeoObject from a JSON string
geo_object_instance = GeoObject.from_json(json)
# print the JSON string representation of the object
print(GeoObject.to_json())

# convert the object into a dict
geo_object_dict = geo_object_instance.to_dict()
# create an instance of GeoObject from a dict
geo_object_from_dict = GeoObject.from_dict(geo_object_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


