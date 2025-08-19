# InternalInformation

Represents internal information about the property, such as access codes and notes.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**access_code** | **str** |  | [optional] 
**note** | **str** |  | [optional] 

## Example

```python
from products.v1.models.internal_information import InternalInformation

# TODO update the JSON string below
json = "{}"
# create an instance of InternalInformation from a JSON string
internal_information_instance = InternalInformation.from_json(json)
# print the JSON string representation of the object
print(InternalInformation.to_json())

# convert the object into a dict
internal_information_dict = internal_information_instance.to_dict()
# create an instance of InternalInformation from a dict
internal_information_from_dict = InternalInformation.from_dict(internal_information_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


