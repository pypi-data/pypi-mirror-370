# RentPartialUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**reference** | **str** |  | [optional] 
**title** | **str** |  | [optional] 
**rent_amount** | **float** |  | [optional] 

## Example

```python
from core.v1.models.rent_partial_update import RentPartialUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of RentPartialUpdate from a JSON string
rent_partial_update_instance = RentPartialUpdate.from_json(json)
# print the JSON string representation of the object
print(RentPartialUpdate.to_json())

# convert the object into a dict
rent_partial_update_dict = rent_partial_update_instance.to_dict()
# create an instance of RentPartialUpdate from a dict
rent_partial_update_from_dict = RentPartialUpdate.from_dict(rent_partial_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


