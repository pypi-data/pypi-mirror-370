# BatchJobIn


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**backend_type_id** | **int** | ID of the batch job | 

## Example

```python
from compute_api_client.models.batch_job_in import BatchJobIn

# TODO update the JSON string below
json = "{}"
# create an instance of BatchJobIn from a JSON string
batch_job_in_instance = BatchJobIn.from_json(json)
# print the JSON string representation of the object
print(BatchJobIn.to_json())

# convert the object into a dict
batch_job_in_dict = batch_job_in_instance.to_dict()
# create an instance of BatchJobIn from a dict
batch_job_in_from_dict = BatchJobIn.from_dict(batch_job_in_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


