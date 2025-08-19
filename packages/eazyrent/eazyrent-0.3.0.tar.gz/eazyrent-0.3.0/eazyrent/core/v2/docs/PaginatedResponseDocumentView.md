# PaginatedResponseDocumentView


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** |  | [optional] [default to 0]
**next** | [**Next**](Next.md) |  | [optional] 
**previous** | [**Previous**](Previous.md) |  | [optional] 
**results** | [**List[DocumentView]**](DocumentView.md) |  | [optional] [default to []]

## Example

```python
from core.v2.models.paginated_response_document_view import PaginatedResponseDocumentView

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResponseDocumentView from a JSON string
paginated_response_document_view_instance = PaginatedResponseDocumentView.from_json(json)
# print the JSON string representation of the object
print(PaginatedResponseDocumentView.to_json())

# convert the object into a dict
paginated_response_document_view_dict = paginated_response_document_view_instance.to_dict()
# create an instance of PaginatedResponseDocumentView from a dict
paginated_response_document_view_from_dict = PaginatedResponseDocumentView.from_dict(paginated_response_document_view_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


