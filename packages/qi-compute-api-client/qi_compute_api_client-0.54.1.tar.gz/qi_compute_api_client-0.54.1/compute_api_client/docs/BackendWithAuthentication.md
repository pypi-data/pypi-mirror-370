# BackendWithAuthentication


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | The id of the backend | 
**name** | **str** | The name of the backend | 
**location** | **str** | The location of the backend | 
**backend_type_id** | **int** | The id of the backend type | 
**status** | [**BackendStatus**](BackendStatus.md) | Status of the backend | 
**last_heartbeat** | **datetime** | Time of last heartbeat | 
**authentication_hash** | **str** | The authentication hash of the backend | 

## Example

```python
from compute_api_client.models.backend_with_authentication import BackendWithAuthentication

# TODO update the JSON string below
json = "{}"
# create an instance of BackendWithAuthentication from a JSON string
backend_with_authentication_instance = BackendWithAuthentication.from_json(json)
# print the JSON string representation of the object
print(BackendWithAuthentication.to_json())

# convert the object into a dict
backend_with_authentication_dict = backend_with_authentication_instance.to_dict()
# create an instance of BackendWithAuthentication from a dict
backend_with_authentication_from_dict = BackendWithAuthentication.from_dict(backend_with_authentication_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


