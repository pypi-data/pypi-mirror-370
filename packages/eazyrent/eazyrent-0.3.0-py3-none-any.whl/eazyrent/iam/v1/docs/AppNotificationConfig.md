# AppNotificationConfig

Manage notifications subscriptions.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rental_file_submitted** | **bool** |  | [optional] [default to True]
**rental_file_created** | **bool** |  | [optional] [default to True]
**rental_file_deletion** | **bool** |  | [optional] [default to True]
**rental_file_analyzed** | **bool** |  | [optional] [default to True]
**rental_file_collected** | **bool** |  | [optional] [default to True]
**insurance_agreement** | **bool** |  | [optional] [default to False]

## Example

```python
from iam.v1.models.app_notification_config import AppNotificationConfig

# TODO update the JSON string below
json = "{}"
# create an instance of AppNotificationConfig from a JSON string
app_notification_config_instance = AppNotificationConfig.from_json(json)
# print the JSON string representation of the object
print(AppNotificationConfig.to_json())

# convert the object into a dict
app_notification_config_dict = app_notification_config_instance.to_dict()
# create an instance of AppNotificationConfig from a dict
app_notification_config_from_dict = AppNotificationConfig.from_dict(app_notification_config_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


