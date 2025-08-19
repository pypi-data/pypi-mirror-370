# ApisCoreSchemasV1PhysicalGuarantorsPhysicalGuarantor


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**first_name** | **str** |  | [optional] 
**last_name** | **str** |  | [optional] 
**email** | **str** |  | [optional] 
**phone** | **str** |  | [optional] 
**added_at** | **datetime** |  | 
**last_update** | **datetime** |  | [optional] 
**external_reference** | **str** |  | [optional] 
**applicant_file** | **str** |  | 
**for_applicant** | **str** |  | 
**status** | **str** |  | [optional] 
**score** | **float** |  | [optional] 

## Example

```python
from core.v1.models.apis_core_schemas_v1_physical_guarantors_physical_guarantor import ApisCoreSchemasV1PhysicalGuarantorsPhysicalGuarantor

# TODO update the JSON string below
json = "{}"
# create an instance of ApisCoreSchemasV1PhysicalGuarantorsPhysicalGuarantor from a JSON string
apis_core_schemas_v1_physical_guarantors_physical_guarantor_instance = ApisCoreSchemasV1PhysicalGuarantorsPhysicalGuarantor.from_json(json)
# print the JSON string representation of the object
print(ApisCoreSchemasV1PhysicalGuarantorsPhysicalGuarantor.to_json())

# convert the object into a dict
apis_core_schemas_v1_physical_guarantors_physical_guarantor_dict = apis_core_schemas_v1_physical_guarantors_physical_guarantor_instance.to_dict()
# create an instance of ApisCoreSchemasV1PhysicalGuarantorsPhysicalGuarantor from a dict
apis_core_schemas_v1_physical_guarantors_physical_guarantor_from_dict = ApisCoreSchemasV1PhysicalGuarantorsPhysicalGuarantor.from_dict(apis_core_schemas_v1_physical_guarantors_physical_guarantor_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


