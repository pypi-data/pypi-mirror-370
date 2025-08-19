# BaseAlertType


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**name** | **str** |  | 
**description** | **str** |  | 

## Example

```python
from iam.v1.models.base_alert_type import BaseAlertType

# TODO update the JSON string below
json = "{}"
# create an instance of BaseAlertType from a JSON string
base_alert_type_instance = BaseAlertType.from_json(json)
# print the JSON string representation of the object
print(BaseAlertType.to_json())

# convert the object into a dict
base_alert_type_dict = base_alert_type_instance.to_dict()
# create an instance of BaseAlertType from a dict
base_alert_type_from_dict = BaseAlertType.from_dict(base_alert_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


