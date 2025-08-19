# FormPartSectionsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**title** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**component** | **str** |  | [optional] [default to 'Markdown']
**mandatory** | **bool** |  | [optional] [default to False]
**display_condition** | [**DisplayCondition**](DisplayCondition.md) |  | [optional] 
**question** | **str** |  | 
**options** | **List[str]** |  | [optional] 
**completed** | **bool** |  | [optional] [default to True]
**response** | **str** |  | [optional] 
**display** | **bool** |  | [optional] [default to True]
**documents** | [**List[DocumentToUpload]**](DocumentToUpload.md) |  | [optional] [default to []]
**min_docs** | **int** |  | [optional] [default to 1]
**uploads** | [**List[TenantUploadedFile]**](TenantUploadedFile.md) |  | [optional] [default to []]
**component_data** | [**MiTrustData**](MiTrustData.md) |  | [optional] 
**errors** | [**List[MiTrustError]**](MiTrustError.md) |  | [optional] [default to []]
**target** | **float** |  | [optional] [default to 0.37]
**user_incomes** | **float** |  | [optional] 
**social_incomes** | **float** |  | [optional] 
**content** | **str** |  | 

## Example

```python
from core.v2.models.form_part_sections_inner import FormPartSectionsInner

# TODO update the JSON string below
json = "{}"
# create an instance of FormPartSectionsInner from a JSON string
form_part_sections_inner_instance = FormPartSectionsInner.from_json(json)
# print the JSON string representation of the object
print(FormPartSectionsInner.to_json())

# convert the object into a dict
form_part_sections_inner_dict = form_part_sections_inner_instance.to_dict()
# create an instance of FormPartSectionsInner from a dict
form_part_sections_inner_from_dict = FormPartSectionsInner.from_dict(form_part_sections_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


