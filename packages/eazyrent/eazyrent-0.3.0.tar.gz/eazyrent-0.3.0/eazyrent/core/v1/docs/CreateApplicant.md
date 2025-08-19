# CreateApplicant


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**first_name** | **str** |  | [optional] 
**last_name** | **str** |  | [optional] 
**email** | **str** |  | [optional] 
**phone** | **str** |  | [optional] 
**external_reference** | **str** |  | [optional] 
**applicant_file** | **str** |  | [optional] 

## Example

```python
from core.v1.models.create_applicant import CreateApplicant

# TODO update the JSON string below
json = "{}"
# create an instance of CreateApplicant from a JSON string
create_applicant_instance = CreateApplicant.from_json(json)
# print the JSON string representation of the object
print(CreateApplicant.to_json())

# convert the object into a dict
create_applicant_dict = create_applicant_instance.to_dict()
# create an instance of CreateApplicant from a dict
create_applicant_from_dict = CreateApplicant.from_dict(create_applicant_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


