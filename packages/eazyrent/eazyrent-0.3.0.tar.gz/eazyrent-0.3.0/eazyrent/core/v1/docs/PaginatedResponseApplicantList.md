# PaginatedResponseApplicantList


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** |  | [optional] [default to 0]
**next** | [**Next**](Next.md) |  | [optional] 
**previous** | [**Previous**](Previous.md) |  | [optional] 
**results** | [**List[ApplicantList]**](ApplicantList.md) |  | [optional] [default to []]

## Example

```python
from core.v1.models.paginated_response_applicant_list import PaginatedResponseApplicantList

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResponseApplicantList from a JSON string
paginated_response_applicant_list_instance = PaginatedResponseApplicantList.from_json(json)
# print the JSON string representation of the object
print(PaginatedResponseApplicantList.to_json())

# convert the object into a dict
paginated_response_applicant_list_dict = paginated_response_applicant_list_instance.to_dict()
# create an instance of PaginatedResponseApplicantList from a dict
paginated_response_applicant_list_from_dict = PaginatedResponseApplicantList.from_dict(paginated_response_applicant_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


