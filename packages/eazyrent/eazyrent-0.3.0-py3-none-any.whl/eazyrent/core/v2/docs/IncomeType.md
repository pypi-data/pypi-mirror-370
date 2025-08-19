# IncomeType


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**raw** | **str** |  | 
**normalized** | **str** |  | 

## Example

```python
from core.v2.models.income_type import IncomeType

# TODO update the JSON string below
json = "{}"
# create an instance of IncomeType from a JSON string
income_type_instance = IncomeType.from_json(json)
# print the JSON string representation of the object
print(IncomeType.to_json())

# convert the object into a dict
income_type_dict = income_type_instance.to_dict()
# create an instance of IncomeType from a dict
income_type_from_dict = IncomeType.from_dict(income_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


