# PageTeam


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[Team]**](Team.md) |  | 
**total** | **int** |  | [optional] 
**page** | **int** |  | 
**size** | **int** |  | 
**pages** | **int** |  | [optional] 

## Example

```python
from compute_api_client.models.page_team import PageTeam

# TODO update the JSON string below
json = "{}"
# create an instance of PageTeam from a JSON string
page_team_instance = PageTeam.from_json(json)
# print the JSON string representation of the object
print(PageTeam.to_json())

# convert the object into a dict
page_team_dict = page_team_instance.to_dict()
# create an instance of PageTeam from a dict
page_team_from_dict = PageTeam.from_dict(page_team_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


