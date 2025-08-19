# PaginatedResponseSupportingDocumentList


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** |  | [optional] [default to 0]
**next** | [**Next**](Next.md) |  | [optional] 
**previous** | [**Previous**](Previous.md) |  | [optional] 
**results** | [**List[SupportingDocumentList]**](SupportingDocumentList.md) |  | [optional] [default to []]

## Example

```python
from core.v1.models.paginated_response_supporting_document_list import PaginatedResponseSupportingDocumentList

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResponseSupportingDocumentList from a JSON string
paginated_response_supporting_document_list_instance = PaginatedResponseSupportingDocumentList.from_json(json)
# print the JSON string representation of the object
print(PaginatedResponseSupportingDocumentList.to_json())

# convert the object into a dict
paginated_response_supporting_document_list_dict = paginated_response_supporting_document_list_instance.to_dict()
# create an instance of PaginatedResponseSupportingDocumentList from a dict
paginated_response_supporting_document_list_from_dict = PaginatedResponseSupportingDocumentList.from_dict(paginated_response_supporting_document_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


