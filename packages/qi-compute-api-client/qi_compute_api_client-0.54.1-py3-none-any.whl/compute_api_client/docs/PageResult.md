# PageResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[Result]**](Result.md) |  | 
**total** | **int** |  | [optional] 
**page** | **int** |  | 
**size** | **int** |  | 
**pages** | **int** |  | [optional] 

## Example

```python
from compute_api_client.models.page_result import PageResult

# TODO update the JSON string below
json = "{}"
# create an instance of PageResult from a JSON string
page_result_instance = PageResult.from_json(json)
# print the JSON string representation of the object
print(PageResult.to_json())

# convert the object into a dict
page_result_dict = page_result_instance.to_dict()
# create an instance of PageResult from a dict
page_result_from_dict = PageResult.from_dict(page_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


