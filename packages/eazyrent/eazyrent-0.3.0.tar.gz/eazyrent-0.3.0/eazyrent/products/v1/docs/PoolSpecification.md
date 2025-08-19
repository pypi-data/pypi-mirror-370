# PoolSpecification


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**length** | **float** |  | [optional] 
**width** | **float** |  | [optional] 
**depth** | **float** |  | [optional] 
**shape** | **str** |  | [optional] 
**materials** | **str** |  | [optional] 
**heating_system** | **str** |  | [optional] 
**construction_date** | **date** |  | [optional] 
**indoor** | **bool** |  | [optional] [default to False]
**safety_compliance** | **bool** |  | [optional] [default to False]

## Example

```python
from products.v1.models.pool_specification import PoolSpecification

# TODO update the JSON string below
json = "{}"
# create an instance of PoolSpecification from a JSON string
pool_specification_instance = PoolSpecification.from_json(json)
# print the JSON string representation of the object
print(PoolSpecification.to_json())

# convert the object into a dict
pool_specification_dict = pool_specification_instance.to_dict()
# create an instance of PoolSpecification from a dict
pool_specification_from_dict = PoolSpecification.from_dict(pool_specification_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


