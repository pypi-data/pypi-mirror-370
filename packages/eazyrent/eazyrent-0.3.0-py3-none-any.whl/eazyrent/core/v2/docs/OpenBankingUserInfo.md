# OpenBankingUserInfo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**finances** | [**ApisExternalServicesSchemasMitrustBankingFinance**](ApisExternalServicesSchemasMitrustBankingFinance.md) |  | 
**financials** | [**Financials**](Financials.md) |  | 
**name** | **str** |  | 
**birthdate** | **date** |  | 

## Example

```python
from core.v2.models.open_banking_user_info import OpenBankingUserInfo

# TODO update the JSON string below
json = "{}"
# create an instance of OpenBankingUserInfo from a JSON string
open_banking_user_info_instance = OpenBankingUserInfo.from_json(json)
# print the JSON string representation of the object
print(OpenBankingUserInfo.to_json())

# convert the object into a dict
open_banking_user_info_dict = open_banking_user_info_instance.to_dict()
# create an instance of OpenBankingUserInfo from a dict
open_banking_user_info_from_dict = OpenBankingUserInfo.from_dict(open_banking_user_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


