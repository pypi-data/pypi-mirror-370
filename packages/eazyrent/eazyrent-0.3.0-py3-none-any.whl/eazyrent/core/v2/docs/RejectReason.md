# RejectReason


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**reason** | **str** |  | 
**comment** | **str** |  | [optional] 

## Example

```python
from core.v2.models.reject_reason import RejectReason

# TODO update the JSON string below
json = "{}"
# create an instance of RejectReason from a JSON string
reject_reason_instance = RejectReason.from_json(json)
# print the JSON string representation of the object
print(RejectReason.to_json())

# convert the object into a dict
reject_reason_dict = reject_reason_instance.to_dict()
# create an instance of RejectReason from a dict
reject_reason_from_dict = RejectReason.from_dict(reject_reason_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


