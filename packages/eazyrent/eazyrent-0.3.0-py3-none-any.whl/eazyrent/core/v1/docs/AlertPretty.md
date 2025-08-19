# AlertPretty


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**alert_type** | **str** |  | 
**document** | **str** |  | 
**document_type** | **str** |  | 
**status** | [**StatusE9dEnum**](StatusE9dEnum.md) |  | [optional] 
**comment** | **str** |  | [optional] 
**code** | **str** |  | 

## Example

```python
from core.v1.models.alert_pretty import AlertPretty

# TODO update the JSON string below
json = "{}"
# create an instance of AlertPretty from a JSON string
alert_pretty_instance = AlertPretty.from_json(json)
# print the JSON string representation of the object
print(AlertPretty.to_json())

# convert the object into a dict
alert_pretty_dict = alert_pretty_instance.to_dict()
# create an instance of AlertPretty from a dict
alert_pretty_from_dict = AlertPretty.from_dict(alert_pretty_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


