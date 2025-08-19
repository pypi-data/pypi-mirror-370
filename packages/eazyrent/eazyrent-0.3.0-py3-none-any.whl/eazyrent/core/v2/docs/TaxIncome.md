# TaxIncome


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tax_notice** | [**TaxNotice**](TaxNotice.md) |  | 

## Example

```python
from core.v2.models.tax_income import TaxIncome

# TODO update the JSON string below
json = "{}"
# create an instance of TaxIncome from a JSON string
tax_income_instance = TaxIncome.from_json(json)
# print the JSON string representation of the object
print(TaxIncome.to_json())

# convert the object into a dict
tax_income_dict = tax_income_instance.to_dict()
# create an instance of TaxIncome from a dict
tax_income_from_dict = TaxIncome.from_dict(tax_income_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


