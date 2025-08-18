# CommitIn


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** | Desriptive message of the commit | 
**algorithm_id** | **int** | ID of the algorithm | 

## Example

```python
from compute_api_client.models.commit_in import CommitIn

# TODO update the JSON string below
json = "{}"
# create an instance of CommitIn from a JSON string
commit_in_instance = CommitIn.from_json(json)
# print the JSON string representation of the object
print(CommitIn.to_json())

# convert the object into a dict
commit_in_dict = commit_in_instance.to_dict()
# create an instance of CommitIn from a dict
commit_in_from_dict = CommitIn.from_dict(commit_in_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


