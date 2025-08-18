# BackendIn


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the backend | 
**location** | **str** | The location of the backend | 
**backend_type_id** | **int** | The id of the backend type | 
**status** | [**BackendStatus**](BackendStatus.md) | Status of the backend | 
**last_heartbeat** | **datetime** | Time of last heartbeat | 

## Example

```python
from compute_api_client.models.backend_in import BackendIn

# TODO update the JSON string below
json = "{}"
# create an instance of BackendIn from a JSON string
backend_in_instance = BackendIn.from_json(json)
# print the JSON string representation of the object
print(BackendIn.to_json())

# convert the object into a dict
backend_in_dict = backend_in_instance.to_dict()
# create an instance of BackendIn from a dict
backend_in_from_dict = BackendIn.from_dict(backend_in_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


