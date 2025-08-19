# RentalFileComment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**tenant** | **str** |  | 
**created_at** | **datetime** |  | [optional] 
**created_by** | **str** |  | 
**comment** | **str** |  | 

## Example

```python
from core.v2.models.rental_file_comment import RentalFileComment

# TODO update the JSON string below
json = "{}"
# create an instance of RentalFileComment from a JSON string
rental_file_comment_instance = RentalFileComment.from_json(json)
# print the JSON string representation of the object
print(RentalFileComment.to_json())

# convert the object into a dict
rental_file_comment_dict = rental_file_comment_instance.to_dict()
# create an instance of RentalFileComment from a dict
rental_file_comment_from_dict = RentalFileComment.from_dict(rental_file_comment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


