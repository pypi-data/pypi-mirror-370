# UserConfig


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email_signature** | **str** |  | [optional] [default to '']
**dark_mode** | **bool** |  | [optional] [default to False]
**property_rent_subscriptions** | [**List[UserConfigPropertyRentSubscriptionsInner]**](UserConfigPropertyRentSubscriptionsInner.md) |  | [optional] [default to []]
**send_notification_by_mail** | **bool** |  | [optional] [default to False]
**raw_html_email** | **bool** |  | [optional] [default to False]
**interface_config** | **object** |  | [optional] 

## Example

```python
from iam.v1.models.user_config import UserConfig

# TODO update the JSON string below
json = "{}"
# create an instance of UserConfig from a JSON string
user_config_instance = UserConfig.from_json(json)
# print the JSON string representation of the object
print(UserConfig.to_json())

# convert the object into a dict
user_config_dict = user_config_instance.to_dict()
# create an instance of UserConfig from a dict
user_config_from_dict = UserConfig.from_dict(user_config_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


