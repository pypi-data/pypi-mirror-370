# Financials


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**accounts** | [**List[BankAccount]**](BankAccount.md) |  | 

## Example

```python
from core.v2.models.financials import Financials

# TODO update the JSON string below
json = "{}"
# create an instance of Financials from a JSON string
financials_instance = Financials.from_json(json)
# print the JSON string representation of the object
print(Financials.to_json())

# convert the object into a dict
financials_dict = financials_instance.to_dict()
# create an instance of Financials from a dict
financials_from_dict = Financials.from_dict(financials_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


