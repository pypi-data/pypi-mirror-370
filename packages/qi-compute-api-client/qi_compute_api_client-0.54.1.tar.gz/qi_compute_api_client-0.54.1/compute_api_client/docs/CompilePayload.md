# CompilePayload


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**compile_stage** | [**CompileStage**](CompileStage.md) |  | [optional] 
**backend_type_id** | **int** | ID of the backendtype | 

## Example

```python
from compute_api_client.models.compile_payload import CompilePayload

# TODO update the JSON string below
json = "{}"
# create an instance of CompilePayload from a JSON string
compile_payload_instance = CompilePayload.from_json(json)
# print the JSON string representation of the object
print(CompilePayload.to_json())

# convert the object into a dict
compile_payload_dict = compile_payload_instance.to_dict()
# create an instance of CompilePayload from a dict
compile_payload_from_dict = CompilePayload.from_dict(compile_payload_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


