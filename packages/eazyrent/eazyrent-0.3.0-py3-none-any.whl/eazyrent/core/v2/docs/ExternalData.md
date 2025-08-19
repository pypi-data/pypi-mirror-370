# ExternalData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**identity** | [**IdentityUserInfo**](IdentityUserInfo.md) |  | [optional] 
**tax** | [**TaxUserInfo**](TaxUserInfo.md) |  | [optional] 
**student** | **object** |  | [optional] 
**open_banking** | [**OpenBankingUserInfo**](OpenBankingUserInfo.md) |  | [optional] 
**other** | **object** |  | [optional] 

## Example

```python
from core.v2.models.external_data import ExternalData

# TODO update the JSON string below
json = "{}"
# create an instance of ExternalData from a JSON string
external_data_instance = ExternalData.from_json(json)
# print the JSON string representation of the object
print(ExternalData.to_json())

# convert the object into a dict
external_data_dict = external_data_instance.to_dict()
# create an instance of ExternalData from a dict
external_data_from_dict = ExternalData.from_dict(external_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


