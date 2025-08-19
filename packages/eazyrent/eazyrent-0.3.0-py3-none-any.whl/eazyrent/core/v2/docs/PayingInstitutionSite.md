# PayingInstitutionSite


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**registration_number** | **str** |  | 

## Example

```python
from core.v2.models.paying_institution_site import PayingInstitutionSite

# TODO update the JSON string below
json = "{}"
# create an instance of PayingInstitutionSite from a JSON string
paying_institution_site_instance = PayingInstitutionSite.from_json(json)
# print the JSON string representation of the object
print(PayingInstitutionSite.to_json())

# convert the object into a dict
paying_institution_site_dict = paying_institution_site_instance.to_dict()
# create an instance of PayingInstitutionSite from a dict
paying_institution_site_from_dict = PayingInstitutionSite.from_dict(paying_institution_site_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


