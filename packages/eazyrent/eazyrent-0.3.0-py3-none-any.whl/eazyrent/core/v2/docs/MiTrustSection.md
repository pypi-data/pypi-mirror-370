# MiTrustSection


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**title** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**component** | **str** |  | [optional] [default to 'MiTrust']
**mandatory** | **bool** |  | [optional] [default to False]
**display_condition** | [**DisplayCondition**](DisplayCondition.md) |  | [optional] 
**component_data** | [**MiTrustData**](MiTrustData.md) |  | [optional] 
**completed** | **bool** |  | [optional] [default to False]
**display** | **bool** |  | [optional] [default to True]
**errors** | [**List[MiTrustError]**](MiTrustError.md) |  | [optional] [default to []]

## Example

```python
from core.v2.models.mi_trust_section import MiTrustSection

# TODO update the JSON string below
json = "{}"
# create an instance of MiTrustSection from a JSON string
mi_trust_section_instance = MiTrustSection.from_json(json)
# print the JSON string representation of the object
print(MiTrustSection.to_json())

# convert the object into a dict
mi_trust_section_dict = mi_trust_section_instance.to_dict()
# create an instance of MiTrustSection from a dict
mi_trust_section_from_dict = MiTrustSection.from_dict(mi_trust_section_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


