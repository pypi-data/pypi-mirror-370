# IncomeRecord


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**paying_institution** | [**PayingInstitution**](PayingInstitution.md) |  | 
**segment** | **str** |  | 
**net_amount** | [**NetAmount**](NetAmount.md) |  | 
**start_date** | **date** |  | 
**end_date** | **date** |  | 
**var_date** | **date** |  | 
**type** | [**IncomeType**](IncomeType.md) |  | 

## Example

```python
from core.v2.models.income_record import IncomeRecord

# TODO update the JSON string below
json = "{}"
# create an instance of IncomeRecord from a JSON string
income_record_instance = IncomeRecord.from_json(json)
# print the JSON string representation of the object
print(IncomeRecord.to_json())

# convert the object into a dict
income_record_dict = income_record_instance.to_dict()
# create an instance of IncomeRecord from a dict
income_record_from_dict = IncomeRecord.from_dict(income_record_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


