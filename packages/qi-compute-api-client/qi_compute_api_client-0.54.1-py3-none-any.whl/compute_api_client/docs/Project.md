# Project


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | The ID of the project | 
**created_on** | **datetime** | Time of creation of the project | 
**owner_id** | **int** | The ID of the project owner | 
**name** | **str** | The name of the project | 
**description** | **str** | The description of the project | 
**starred** | **bool** | If the project is starred | 

## Example

```python
from compute_api_client.models.project import Project

# TODO update the JSON string below
json = "{}"
# create an instance of Project from a JSON string
project_instance = Project.from_json(json)
# print the JSON string representation of the object
print(Project.to_json())

# convert the object into a dict
project_dict = project_instance.to_dict()
# create an instance of Project from a dict
project_from_dict = Project.from_dict(project_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


