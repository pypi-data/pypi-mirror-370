# MiTrustError


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **str** |  | 
**message** | **str** |  | 
**handled** | **bool** |  | [optional] [default to False]

## Example

```python
from core.v2.models.mi_trust_error import MiTrustError

# TODO update the JSON string below
json = "{}"
# create an instance of MiTrustError from a JSON string
mi_trust_error_instance = MiTrustError.from_json(json)
# print the JSON string representation of the object
print(MiTrustError.to_json())

# convert the object into a dict
mi_trust_error_dict = mi_trust_error_instance.to_dict()
# create an instance of MiTrustError from a dict
mi_trust_error_from_dict = MiTrustError.from_dict(mi_trust_error_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


