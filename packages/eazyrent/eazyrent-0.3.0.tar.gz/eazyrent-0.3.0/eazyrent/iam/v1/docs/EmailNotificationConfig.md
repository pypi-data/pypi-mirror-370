# EmailNotificationConfig


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rental_file_submitted** | **bool** |  | [optional] [default to False]
**rental_file_created** | **bool** |  | [optional] [default to False]
**rental_file_deletion** | **bool** |  | [optional] [default to False]
**rental_file_analyzed** | **bool** |  | [optional] [default to False]
**rental_file_collected** | **bool** |  | [optional] [default to False]
**insurance_agreement** | **bool** |  | [optional] [default to False]
**notifications_overview** | **bool** |  | [optional] [default to True]

## Example

```python
from iam.v1.models.email_notification_config import EmailNotificationConfig

# TODO update the JSON string below
json = "{}"
# create an instance of EmailNotificationConfig from a JSON string
email_notification_config_instance = EmailNotificationConfig.from_json(json)
# print the JSON string representation of the object
print(EmailNotificationConfig.to_json())

# convert the object into a dict
email_notification_config_dict = email_notification_config_instance.to_dict()
# create an instance of EmailNotificationConfig from a dict
email_notification_config_from_dict = EmailNotificationConfig.from_dict(email_notification_config_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


