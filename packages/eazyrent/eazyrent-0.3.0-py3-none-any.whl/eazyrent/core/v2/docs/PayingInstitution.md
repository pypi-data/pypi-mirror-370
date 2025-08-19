# PayingInstitution


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**registration_status** | **str** |  | 
**business_sector_code** | **str** |  | 
**registration_date** | **date** |  | 
**legal_business_name** | **str** |  | 
**site** | [**PayingInstitutionSite**](PayingInstitutionSite.md) |  | 
**legal_form** | **str** |  | 
**registration_number** | **str** |  | 
**address** | [**Address**](Address.md) |  | 

## Example

```python
from core.v2.models.paying_institution import PayingInstitution

# TODO update the JSON string below
json = "{}"
# create an instance of PayingInstitution from a JSON string
paying_institution_instance = PayingInstitution.from_json(json)
# print the JSON string representation of the object
print(PayingInstitution.to_json())

# convert the object into a dict
paying_institution_dict = paying_institution_instance.to_dict()
# create an instance of PayingInstitution from a dict
paying_institution_from_dict = PayingInstitution.from_dict(paying_institution_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


