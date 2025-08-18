# PageBackendType


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[BackendType]**](BackendType.md) |  | 
**total** | **int** |  | [optional] 
**page** | **int** |  | 
**size** | **int** |  | 
**pages** | **int** |  | [optional] 

## Example

```python
from compute_api_client.models.page_backend_type import PageBackendType

# TODO update the JSON string below
json = "{}"
# create an instance of PageBackendType from a JSON string
page_backend_type_instance = PageBackendType.from_json(json)
# print the JSON string representation of the object
print(PageBackendType.to_json())

# convert the object into a dict
page_backend_type_dict = page_backend_type_instance.to_dict()
# create an instance of PageBackendType from a dict
page_backend_type_from_dict = PageBackendType.from_dict(page_backend_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


