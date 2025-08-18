# Job


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | The ID of the job | 
**created_on** | **datetime** | Time of creation of the Job | 
**file_id** | **int** | The ID of the file | 
**algorithm_type** | [**AlgorithmType**](AlgorithmType.md) | The type of the algorithm | 
**status** | [**JobStatus**](JobStatus.md) | The status of the Job | 
**batch_job_id** | **int** | The ID of the batch job | 
**queued_at** | **datetime** |  | 
**finished_at** | **datetime** |  | 
**number_of_shots** | **int** |  | 
**raw_data_enabled** | **bool** | If raw data is to be attached to results | 
**session_id** | **str** | The uuid assigned to the job | 
**trace_id** | **str** | The uuid of the trace in case of job failure | 
**message** | **str** | The message associated with the executed job if it failed | 
**source** | **str** | The source application of an exception that caused a job to fail (if applicable). | [optional] [default to '']

## Example

```python
from compute_api_client.models.job import Job

# TODO update the JSON string below
json = "{}"
# create an instance of Job from a JSON string
job_instance = Job.from_json(json)
# print the JSON string representation of the object
print(Job.to_json())

# convert the object into a dict
job_dict = job_instance.to_dict()
# create an instance of Job from a dict
job_from_dict = Job.from_dict(job_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


