# PagePermission


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[Permission]**](Permission.md) |  | 
**total** | **int** |  | [optional] 
**page** | **int** |  | 
**size** | **int** |  | 
**pages** | **int** |  | [optional] 

## Example

```python
from compute_api_client.models.page_permission import PagePermission

# TODO update the JSON string below
json = "{}"
# create an instance of PagePermission from a JSON string
page_permission_instance = PagePermission.from_json(json)
# print the JSON string representation of the object
print(PagePermission.to_json())

# convert the object into a dict
page_permission_dict = page_permission_instance.to_dict()
# create an instance of PagePermission from a dict
page_permission_from_dict = PagePermission.from_dict(page_permission_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


