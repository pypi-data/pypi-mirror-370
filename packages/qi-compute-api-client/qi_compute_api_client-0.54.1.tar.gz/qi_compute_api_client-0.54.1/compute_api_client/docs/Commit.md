# Commit


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | ID of the commit | 
**created_on** | **datetime** | Time of creation of the commit | 
**hash** | **str** | Unique hash assigned to the commit | 
**description** | **str** | Desriptive message of the commit | 
**algorithm_id** | **int** | ID of the algorithm | 

## Example

```python
from compute_api_client.models.commit import Commit

# TODO update the JSON string below
json = "{}"
# create an instance of Commit from a JSON string
commit_instance = Commit.from_json(json)
# print the JSON string representation of the object
print(Commit.to_json())

# convert the object into a dict
commit_dict = commit_instance.to_dict()
# create an instance of Commit from a dict
commit_from_dict = Commit.from_dict(commit_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


