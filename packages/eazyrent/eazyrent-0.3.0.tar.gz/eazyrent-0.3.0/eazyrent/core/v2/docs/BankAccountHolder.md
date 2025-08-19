# BankAccountHolder


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 

## Example

```python
from core.v2.models.bank_account_holder import BankAccountHolder

# TODO update the JSON string below
json = "{}"
# create an instance of BankAccountHolder from a JSON string
bank_account_holder_instance = BankAccountHolder.from_json(json)
# print the JSON string representation of the object
print(BankAccountHolder.to_json())

# convert the object into a dict
bank_account_holder_dict = bank_account_holder_instance.to_dict()
# create an instance of BankAccountHolder from a dict
bank_account_holder_from_dict = BankAccountHolder.from_dict(bank_account_holder_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


