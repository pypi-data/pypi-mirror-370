# PageAlgorithm


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[Algorithm]**](Algorithm.md) |  | 
**total** | **int** |  | [optional] 
**page** | **int** |  | 
**size** | **int** |  | 
**pages** | **int** |  | [optional] 

## Example

```python
from compute_api_client.models.page_algorithm import PageAlgorithm

# TODO update the JSON string below
json = "{}"
# create an instance of PageAlgorithm from a JSON string
page_algorithm_instance = PageAlgorithm.from_json(json)
# print the JSON string representation of the object
print(PageAlgorithm.to_json())

# convert the object into a dict
page_algorithm_dict = page_algorithm_instance.to_dict()
# create an instance of PageAlgorithm from a dict
page_algorithm_from_dict = PageAlgorithm.from_dict(page_algorithm_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


