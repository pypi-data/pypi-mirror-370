# InvitePayload

Schema for invitation

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**product_id** | **str** |  | 
**email** | **str** |  | 
**first_name** | **str** |  | [optional] 
**last_name** | **str** |  | [optional] 

## Example

```python
from core.v2.models.invite_payload import InvitePayload

# TODO update the JSON string below
json = "{}"
# create an instance of InvitePayload from a JSON string
invite_payload_instance = InvitePayload.from_json(json)
# print the JSON string representation of the object
print(InvitePayload.to_json())

# convert the object into a dict
invite_payload_dict = invite_payload_instance.to_dict()
# create an instance of InvitePayload from a dict
invite_payload_from_dict = InvitePayload.from_dict(invite_payload_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


