# ListProductsProjection


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**achived_at** | **datetime** |  | [optional] 
**category** | [**ProductType**](ProductType.md) |  | [optional] 
**title** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**reference** | **str** |  | [optional] 
**available** | **bool** | Indicates whether the property is currently available. | [optional] [default to True]
**availability** | **date** |  | [optional] 
**exclusivity** | **bool** |  | [optional] 
**disable_spontaneous_applications** | **bool** |  | [optional] 
**managers** | **List[str]** |  | [optional] [default to []]
**meta** | **object** |  | [optional] 
**id** | **str** |  | 
**tenant** | **str** |  | 
**created_at** | **datetime** |  | 
**updated_at** | **datetime** |  | 
**mandate_type** | **str** | The type of mandate for the property. | [optional] [default to 'management']
**price** | **float** |  | [optional] 
**fee** | **float** |  | [optional] 
**fee_type** | **str** | The type of fee arrangement (e.g., direct or reverse). | [optional] [default to 'direct']
**photo** | [**ProductPhoto**](ProductPhoto.md) |  | [optional] 
**incoming_requests** | **int** |  | [optional] [default to 0]
**rent_amount** | **float** |  | [optional] 
**monthly_charges** | **float** |  | [optional] 
**furnished** | **bool** | Indicates whether the property is furnished. | [optional] [default to False]
**warranty_amount** | **float** |  | [optional] 
**agency_fees** | **float** |  | [optional] 
**unpaid_rent_insurance** | **bool** |  | [optional] 

## Example

```python
from core.v2.models.list_products_projection import ListProductsProjection

# TODO update the JSON string below
json = "{}"
# create an instance of ListProductsProjection from a JSON string
list_products_projection_instance = ListProductsProjection.from_json(json)
# print the JSON string representation of the object
print(ListProductsProjection.to_json())

# convert the object into a dict
list_products_projection_dict = list_products_projection_instance.to_dict()
# create an instance of ListProductsProjection from a dict
list_products_projection_from_dict = ListProductsProjection.from_dict(list_products_projection_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


