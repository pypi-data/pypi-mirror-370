# Wage


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**period** | **str** |  | 
**amount** | **float** |  | 

## Example

```python
from core.v2.models.wage import Wage

# TODO update the JSON string below
json = "{}"
# create an instance of Wage from a JSON string
wage_instance = Wage.from_json(json)
# print the JSON string representation of the object
print(Wage.to_json())

# convert the object into a dict
wage_dict = wage_instance.to_dict()
# create an instance of Wage from a dict
wage_from_dict = Wage.from_dict(wage_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


