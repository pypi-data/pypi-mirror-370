# AcceptedSupportingDocument


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**name** | **str** |  | 
**max_accepted_files** | **int** |  | [optional] 
**analyze_as** | **str** |  | 
**analyzed** | **bool** |  | [optional] [default to False]
**category** | **str** |  | [optional] 
**category_name** | **str** |  | [optional] 
**company_config** | [**CompanyConfig**](CompanyConfig.md) |  | 
**display_name** | **str** |  | 

## Example

```python
from core.v1.models.accepted_supporting_document import AcceptedSupportingDocument

# TODO update the JSON string below
json = "{}"
# create an instance of AcceptedSupportingDocument from a JSON string
accepted_supporting_document_instance = AcceptedSupportingDocument.from_json(json)
# print the JSON string representation of the object
print(AcceptedSupportingDocument.to_json())

# convert the object into a dict
accepted_supporting_document_dict = accepted_supporting_document_instance.to_dict()
# create an instance of AcceptedSupportingDocument from a dict
accepted_supporting_document_from_dict = AcceptedSupportingDocument.from_dict(accepted_supporting_document_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


