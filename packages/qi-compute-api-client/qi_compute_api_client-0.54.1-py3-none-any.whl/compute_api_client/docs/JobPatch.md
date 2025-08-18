# JobPatch


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**JobStatus**](JobStatus.md) | The status of the Job | 
**session_id** | **str** | The uuid assigned to the job | [optional] [default to '']
**trace_id** | **str** | The uuid of the trace in case of job failure | [optional] [default to '']
**message** | **str** | The message associated with the executed job if it failed | [optional] [default to '']
**source** | **str** | The source application of an exception that caused a job to fail (if applicable). | [optional] [default to '']
**traceback** | **str** | The traceback of the exception | [optional] [default to '']

## Example

```python
from compute_api_client.models.job_patch import JobPatch

# TODO update the JSON string below
json = "{}"
# create an instance of JobPatch from a JSON string
job_patch_instance = JobPatch.from_json(json)
# print the JSON string representation of the object
print(JobPatch.to_json())

# convert the object into a dict
job_patch_dict = job_patch_instance.to_dict()
# create an instance of JobPatch from a dict
job_patch_from_dict = JobPatch.from_dict(job_patch_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


