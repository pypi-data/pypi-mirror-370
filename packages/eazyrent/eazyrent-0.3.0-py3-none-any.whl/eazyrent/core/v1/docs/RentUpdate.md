# RentUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**reference** | **str** |  | [optional] 
**title** | **str** |  | 
**rent_amount** | **float** |  | 

## Example

```python
from core.v1.models.rent_update import RentUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of RentUpdate from a JSON string
rent_update_instance = RentUpdate.from_json(json)
# print the JSON string representation of the object
print(RentUpdate.to_json())

# convert the object into a dict
rent_update_dict = rent_update_instance.to_dict()
# create an instance of RentUpdate from a dict
rent_update_from_dict = RentUpdate.from_dict(rent_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


