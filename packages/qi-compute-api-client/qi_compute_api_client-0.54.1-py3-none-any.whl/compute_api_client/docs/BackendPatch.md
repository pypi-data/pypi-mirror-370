# BackendPatch


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**BackendStatus**](BackendStatus.md) | Status of the backend | 
**last_heartbeat** | **datetime** | Time of last heartbeat | 

## Example

```python
from compute_api_client.models.backend_patch import BackendPatch

# TODO update the JSON string below
json = "{}"
# create an instance of BackendPatch from a JSON string
backend_patch_instance = BackendPatch.from_json(json)
# print the JSON string representation of the object
print(BackendPatch.to_json())

# convert the object into a dict
backend_patch_dict = backend_patch_instance.to_dict()
# create an instance of BackendPatch from a dict
backend_patch_from_dict = BackendPatch.from_dict(backend_patch_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


