# PaginatedResponseAcceptedSupportingDocument


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** |  | [optional] [default to 0]
**next** | [**Next**](Next.md) |  | [optional] 
**previous** | [**Previous**](Previous.md) |  | [optional] 
**results** | [**List[AcceptedSupportingDocument]**](AcceptedSupportingDocument.md) |  | [optional] [default to []]

## Example

```python
from core.v1.models.paginated_response_accepted_supporting_document import PaginatedResponseAcceptedSupportingDocument

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResponseAcceptedSupportingDocument from a JSON string
paginated_response_accepted_supporting_document_instance = PaginatedResponseAcceptedSupportingDocument.from_json(json)
# print the JSON string representation of the object
print(PaginatedResponseAcceptedSupportingDocument.to_json())

# convert the object into a dict
paginated_response_accepted_supporting_document_dict = paginated_response_accepted_supporting_document_instance.to_dict()
# create an instance of PaginatedResponseAcceptedSupportingDocument from a dict
paginated_response_accepted_supporting_document_from_dict = PaginatedResponseAcceptedSupportingDocument.from_dict(paginated_response_accepted_supporting_document_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


