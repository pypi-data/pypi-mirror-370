# TaxNotice


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**declarers** | **object** |  | 
**property_income_net_amount** | **object** |  | 
**postal_address** | [**Address**](Address.md) |  | 

## Example

```python
from core.v2.models.tax_notice import TaxNotice

# TODO update the JSON string below
json = "{}"
# create an instance of TaxNotice from a JSON string
tax_notice_instance = TaxNotice.from_json(json)
# print the JSON string representation of the object
print(TaxNotice.to_json())

# convert the object into a dict
tax_notice_dict = tax_notice_instance.to_dict()
# create an instance of TaxNotice from a dict
tax_notice_from_dict = TaxNotice.from_dict(tax_notice_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


