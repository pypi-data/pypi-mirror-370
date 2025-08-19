# PhysicalGuarantorCreate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**first_name** | **str** |  | [optional] 
**last_name** | **str** |  | [optional] 
**email** | **str** |  | [optional] 
**phone** | **str** |  | [optional] 
**external_reference** | **str** |  | [optional] 
**for_applicant** | **str** |  | 

## Example

```python
from core.v1.models.physical_guarantor_create import PhysicalGuarantorCreate

# TODO update the JSON string below
json = "{}"
# create an instance of PhysicalGuarantorCreate from a JSON string
physical_guarantor_create_instance = PhysicalGuarantorCreate.from_json(json)
# print the JSON string representation of the object
print(PhysicalGuarantorCreate.to_json())

# convert the object into a dict
physical_guarantor_create_dict = physical_guarantor_create_instance.to_dict()
# create an instance of PhysicalGuarantorCreate from a dict
physical_guarantor_create_from_dict = PhysicalGuarantorCreate.from_dict(physical_guarantor_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


