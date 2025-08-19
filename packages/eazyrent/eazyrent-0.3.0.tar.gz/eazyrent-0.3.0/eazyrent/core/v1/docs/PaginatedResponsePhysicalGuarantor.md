# PaginatedResponsePhysicalGuarantor


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** |  | [optional] [default to 0]
**next** | [**Next**](Next.md) |  | [optional] 
**previous** | [**Previous**](Previous.md) |  | [optional] 
**results** | [**List[ApisCoreSchemasV1PhysicalGuarantorsPhysicalGuarantor]**](ApisCoreSchemasV1PhysicalGuarantorsPhysicalGuarantor.md) |  | [optional] [default to []]

## Example

```python
from core.v1.models.paginated_response_physical_guarantor import PaginatedResponsePhysicalGuarantor

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResponsePhysicalGuarantor from a JSON string
paginated_response_physical_guarantor_instance = PaginatedResponsePhysicalGuarantor.from_json(json)
# print the JSON string representation of the object
print(PaginatedResponsePhysicalGuarantor.to_json())

# convert the object into a dict
paginated_response_physical_guarantor_dict = paginated_response_physical_guarantor_instance.to_dict()
# create an instance of PaginatedResponsePhysicalGuarantor from a dict
paginated_response_physical_guarantor_from_dict = PaginatedResponsePhysicalGuarantor.from_dict(paginated_response_physical_guarantor_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


