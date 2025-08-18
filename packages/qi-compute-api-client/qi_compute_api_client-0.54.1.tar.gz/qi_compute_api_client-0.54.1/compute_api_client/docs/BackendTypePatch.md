# BackendTypePatch


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**infrastructure** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**image_id** | **str** |  | [optional] 
**is_hardware** | **bool** |  | [optional] 
**supports_raw_data** | **bool** |  | [optional] 
**features** | **List[str]** |  | [optional] 
**default_compiler_config** | **Dict[str, object]** |  | [optional] 
**gateset** | **List[str]** |  | [optional] 
**topology** | **List[List[int]]** |  | [optional] 
**nqubits** | **int** |  | [optional] 
**default_number_of_shots** | **int** |  | [optional] 
**max_number_of_shots** | **int** |  | [optional] 
**enabled** | **bool** |  | [optional] 
**identifier** | **str** |  | [optional] 
**protocol_version** | **int** |  | [optional] 

## Example

```python
from compute_api_client.models.backend_type_patch import BackendTypePatch

# TODO update the JSON string below
json = "{}"
# create an instance of BackendTypePatch from a JSON string
backend_type_patch_instance = BackendTypePatch.from_json(json)
# print the JSON string representation of the object
print(BackendTypePatch.to_json())

# convert the object into a dict
backend_type_patch_dict = backend_type_patch_instance.to_dict()
# create an instance of BackendTypePatch from a dict
backend_type_patch_from_dict = BackendTypePatch.from_dict(backend_type_patch_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


