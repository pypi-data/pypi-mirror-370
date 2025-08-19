# HistoryEvent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**event_type** | **str** |  | 
**timestamp** | **datetime** |  | [optional] 
**actor** | **str** |  | [optional] 
**payload** | **object** |  | [optional] 

## Example

```python
from core.v2.models.history_event import HistoryEvent

# TODO update the JSON string below
json = "{}"
# create an instance of HistoryEvent from a JSON string
history_event_instance = HistoryEvent.from_json(json)
# print the JSON string representation of the object
print(HistoryEvent.to_json())

# convert the object into a dict
history_event_dict = history_event_instance.to_dict()
# create an instance of HistoryEvent from a dict
history_event_from_dict = HistoryEvent.from_dict(history_event_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


