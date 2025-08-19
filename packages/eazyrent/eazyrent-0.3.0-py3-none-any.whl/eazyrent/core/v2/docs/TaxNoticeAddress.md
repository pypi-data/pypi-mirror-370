# TaxNoticeAddress


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**country** | **str** |  | 
**formatted** | **str** |  | 

## Example

```python
from core.v2.models.tax_notice_address import TaxNoticeAddress

# TODO update the JSON string below
json = "{}"
# create an instance of TaxNoticeAddress from a JSON string
tax_notice_address_instance = TaxNoticeAddress.from_json(json)
# print the JSON string representation of the object
print(TaxNoticeAddress.to_json())

# convert the object into a dict
tax_notice_address_dict = tax_notice_address_instance.to_dict()
# create an instance of TaxNoticeAddress from a dict
tax_notice_address_from_dict = TaxNoticeAddress.from_dict(tax_notice_address_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


