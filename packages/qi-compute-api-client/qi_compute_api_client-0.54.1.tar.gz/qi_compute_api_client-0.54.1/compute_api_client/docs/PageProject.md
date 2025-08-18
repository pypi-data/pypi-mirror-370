# PageProject


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[Project]**](Project.md) |  | 
**total** | **int** |  | [optional] 
**page** | **int** |  | 
**size** | **int** |  | 
**pages** | **int** |  | [optional] 

## Example

```python
from compute_api_client.models.page_project import PageProject

# TODO update the JSON string below
json = "{}"
# create an instance of PageProject from a JSON string
page_project_instance = PageProject.from_json(json)
# print the JSON string representation of the object
print(PageProject.to_json())

# convert the object into a dict
page_project_dict = page_project_instance.to_dict()
# create an instance of PageProject from a dict
page_project_from_dict = PageProject.from_dict(page_project_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


