# PageCommit


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[Commit]**](Commit.md) |  | 
**total** | **int** |  | [optional] 
**page** | **int** |  | 
**size** | **int** |  | 
**pages** | **int** |  | [optional] 

## Example

```python
from compute_api_client.models.page_commit import PageCommit

# TODO update the JSON string below
json = "{}"
# create an instance of PageCommit from a JSON string
page_commit_instance = PageCommit.from_json(json)
# print the JSON string representation of the object
print(PageCommit.to_json())

# convert the object into a dict
page_commit_dict = page_commit_instance.to_dict()
# create an instance of PageCommit from a dict
page_commit_from_dict = PageCommit.from_dict(page_commit_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


