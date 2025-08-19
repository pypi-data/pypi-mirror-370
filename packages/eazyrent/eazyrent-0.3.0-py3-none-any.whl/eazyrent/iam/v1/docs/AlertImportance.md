# AlertImportance


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**alert_type** | [**BaseAlertType**](BaseAlertType.md) |  | 
**value** | **float** |  | [optional] [default to 0.5]

## Example

```python
from iam.v1.models.alert_importance import AlertImportance

# TODO update the JSON string below
json = "{}"
# create an instance of AlertImportance from a JSON string
alert_importance_instance = AlertImportance.from_json(json)
# print the JSON string representation of the object
print(AlertImportance.to_json())

# convert the object into a dict
alert_importance_dict = alert_importance_instance.to_dict()
# create an instance of AlertImportance from a dict
alert_importance_from_dict = AlertImportance.from_dict(alert_importance_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


