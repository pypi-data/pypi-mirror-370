# Result


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | The ID of the result | 
**created_on** | **datetime** | Time of creation of the result | 
**job_id** | **int** | The ID of the job | 
**execution_time_in_seconds** | **float** | Time it took to compute the result | 
**shots_requested** | **int** |  | 
**shots_done** | **int** |  | 
**results** | **Dict[str, object]** |  | 
**raw_data** | **List[str]** |  | 

## Example

```python
from compute_api_client.models.result import Result

# TODO update the JSON string below
json = "{}"
# create an instance of Result from a JSON string
result_instance = Result.from_json(json)
# print the JSON string representation of the object
print(Result.to_json())

# convert the object into a dict
result_dict = result_instance.to_dict()
# create an instance of Result from a dict
result_from_dict = Result.from_dict(result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


