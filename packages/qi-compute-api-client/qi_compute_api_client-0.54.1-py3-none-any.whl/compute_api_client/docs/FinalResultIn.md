# FinalResultIn


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_id** | **int** | ID of the job | 
**final_result** | **Dict[str, object]** | The final results of the job | 

## Example

```python
from compute_api_client.models.final_result_in import FinalResultIn

# TODO update the JSON string below
json = "{}"
# create an instance of FinalResultIn from a JSON string
final_result_in_instance = FinalResultIn.from_json(json)
# print the JSON string representation of the object
print(FinalResultIn.to_json())

# convert the object into a dict
final_result_in_dict = final_result_in_instance.to_dict()
# create an instance of FinalResultIn from a dict
final_result_in_from_dict = FinalResultIn.from_dict(final_result_in_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


