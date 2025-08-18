# PagePermissionGroup


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[PermissionGroup]**](PermissionGroup.md) |  | 
**total** | **int** |  | [optional] 
**page** | **int** |  | 
**size** | **int** |  | 
**pages** | **int** |  | [optional] 

## Example

```python
from compute_api_client.models.page_permission_group import PagePermissionGroup

# TODO update the JSON string below
json = "{}"
# create an instance of PagePermissionGroup from a JSON string
page_permission_group_instance = PagePermissionGroup.from_json(json)
# print the JSON string representation of the object
print(PagePermissionGroup.to_json())

# convert the object into a dict
page_permission_group_dict = page_permission_group_instance.to_dict()
# create an instance of PagePermissionGroup from a dict
page_permission_group_from_dict = PagePermissionGroup.from_dict(page_permission_group_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


