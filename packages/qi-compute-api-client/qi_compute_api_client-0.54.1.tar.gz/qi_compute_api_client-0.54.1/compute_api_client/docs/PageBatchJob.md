# PageBatchJob


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[BatchJob]**](BatchJob.md) |  | 
**total** | **int** |  | [optional] 
**page** | **int** |  | 
**size** | **int** |  | 
**pages** | **int** |  | [optional] 

## Example

```python
from compute_api_client.models.page_batch_job import PageBatchJob

# TODO update the JSON string below
json = "{}"
# create an instance of PageBatchJob from a JSON string
page_batch_job_instance = PageBatchJob.from_json(json)
# print the JSON string representation of the object
print(PageBatchJob.to_json())

# convert the object into a dict
page_batch_job_dict = page_batch_job_instance.to_dict()
# create an instance of PageBatchJob from a dict
page_batch_job_from_dict = PageBatchJob.from_dict(page_batch_job_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


