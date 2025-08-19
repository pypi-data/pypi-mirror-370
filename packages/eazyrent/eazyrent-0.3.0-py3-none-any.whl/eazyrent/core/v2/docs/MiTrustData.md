# MiTrustData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**client_id** | **str** |  | [optional] [default to '']
**redirect_uri** | **str** |  | [optional] [default to '/oauth/callback/mitrust/']
**scope** | **List[str]** |  | [optional] [default to []]
**assets** | **List[str]** |  | [optional] [default to []]

## Example

```python
from core.v2.models.mi_trust_data import MiTrustData

# TODO update the JSON string below
json = "{}"
# create an instance of MiTrustData from a JSON string
mi_trust_data_instance = MiTrustData.from_json(json)
# print the JSON string representation of the object
print(MiTrustData.to_json())

# convert the object into a dict
mi_trust_data_dict = mi_trust_data_instance.to_dict()
# create an instance of MiTrustData from a dict
mi_trust_data_from_dict = MiTrustData.from_dict(mi_trust_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


