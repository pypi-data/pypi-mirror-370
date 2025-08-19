# TaxUserInfo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**finances** | [**ApisExternalServicesSchemasMitrustTaxFinance**](ApisExternalServicesSchemasMitrustTaxFinance.md) |  | 
**tax** | [**Tax**](Tax.md) |  | 
**name** | **str** |  | 
**given_name** | **str** |  | 
**family_name** | **str** |  | 
**address** | [**TaxNoticeAddress**](TaxNoticeAddress.md) |  | 
**birthdate** | **date** |  | 

## Example

```python
from core.v2.models.tax_user_info import TaxUserInfo

# TODO update the JSON string below
json = "{}"
# create an instance of TaxUserInfo from a JSON string
tax_user_info_instance = TaxUserInfo.from_json(json)
# print the JSON string representation of the object
print(TaxUserInfo.to_json())

# convert the object into a dict
tax_user_info_dict = tax_user_info_instance.to_dict()
# create an instance of TaxUserInfo from a dict
tax_user_info_from_dict = TaxUserInfo.from_dict(tax_user_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


