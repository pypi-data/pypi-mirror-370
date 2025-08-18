# BatchJob


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | ID of the batch job | 
**created_on** | **datetime** | Time of batchjob creation | 
**status** | [**BatchJobStatus**](BatchJobStatus.md) | Status of the batchjob | 
**user_id** | **int** | ID of the user to whom this job belongs | 
**backend_type_id** | **int** | ID of the backendtype | 
**backend_id** | **int** |  | 
**queued_at** | **datetime** |  | 
**reserved_at** | **datetime** |  | 
**finished_at** | **datetime** |  | 
**job_ids** | **List[int]** | Job ids in the batch job | 
**aggregated_algorithm_type** | [**AlgorithmType**](AlgorithmType.md) | Algorithm type submitted | 

## Example

```python
from compute_api_client.models.batch_job import BatchJob

# TODO update the JSON string below
json = "{}"
# create an instance of BatchJob from a JSON string
batch_job_instance = BatchJob.from_json(json)
# print the JSON string representation of the object
print(BatchJob.to_json())

# convert the object into a dict
batch_job_dict = batch_job_instance.to_dict()
# create an instance of BatchJob from a dict
batch_job_from_dict = BatchJob.from_dict(batch_job_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


