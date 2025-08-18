# PageBackend


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[Backend]**](Backend.md) |  | 
**total** | **int** |  | [optional] 
**page** | **int** |  | 
**size** | **int** |  | 
**pages** | **int** |  | [optional] 

## Example

```python
from compute_api_client.models.page_backend import PageBackend

# TODO update the JSON string below
json = "{}"
# create an instance of PageBackend from a JSON string
page_backend_instance = PageBackend.from_json(json)
# print the JSON string representation of the object
print(PageBackend.to_json())

# convert the object into a dict
page_backend_dict = page_backend_instance.to_dict()
# create an instance of PageBackend from a dict
page_backend_from_dict = PageBackend.from_dict(page_backend_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


