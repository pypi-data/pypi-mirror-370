# Backend


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | The id of the backend | 
**name** | **str** | The name of the backend | 
**location** | **str** | The location of the backend | 
**backend_type_id** | **int** | The id of the backend type | 
**status** | [**BackendStatus**](BackendStatus.md) | Status of the backend | 
**last_heartbeat** | **datetime** | Time of last heartbeat | 

## Example

```python
from compute_api_client.models.backend import Backend

# TODO update the JSON string below
json = "{}"
# create an instance of Backend from a JSON string
backend_instance = Backend.from_json(json)
# print the JSON string representation of the object
print(Backend.to_json())

# convert the object into a dict
backend_dict = backend_instance.to_dict()
# create an instance of Backend from a dict
backend_from_dict = Backend.from_dict(backend_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


