# PaginatedResponseListAcceptedDocument


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** |  | [optional] [default to 0]
**next** | [**Next**](Next.md) |  | [optional] 
**previous** | [**Previous**](Previous.md) |  | [optional] 
**results** | [**List[ListAcceptedDocument]**](ListAcceptedDocument.md) |  | [optional] [default to []]

## Example

```python
from core.v2.models.paginated_response_list_accepted_document import PaginatedResponseListAcceptedDocument

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResponseListAcceptedDocument from a JSON string
paginated_response_list_accepted_document_instance = PaginatedResponseListAcceptedDocument.from_json(json)
# print the JSON string representation of the object
print(PaginatedResponseListAcceptedDocument.to_json())

# convert the object into a dict
paginated_response_list_accepted_document_dict = paginated_response_list_accepted_document_instance.to_dict()
# create an instance of PaginatedResponseListAcceptedDocument from a dict
paginated_response_list_accepted_document_from_dict = PaginatedResponseListAcceptedDocument.from_dict(paginated_response_list_accepted_document_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


