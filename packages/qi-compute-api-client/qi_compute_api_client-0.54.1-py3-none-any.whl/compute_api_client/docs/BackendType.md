# BackendType


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | The id of the backend type | 
**name** | **str** | Name of the backend type | 
**infrastructure** | **str** | Name of the infrastructure | 
**description** | **str** | Description of the backendtype | 
**image_id** | **str** | The id of the image | 
**is_hardware** | **bool** | If it is hardware | 
**supports_raw_data** | **bool** | If it supports raw data extraction | 
**features** | **List[Optional[str]]** | The features supported by backend type | 
**default_compiler_config** | **Dict[str, object]** | The various passes for each stage | 
**gateset** | **List[Optional[str]]** | The primary gatesets supported by the backend | 
**topology** | **List[List[int]]** | The topology of the backend | 
**nqubits** | **int** | The number of qubits on the backend | 
**status** | [**BackendStatus**](BackendStatus.md) | The status of the backend type | 
**default_number_of_shots** | **int** | The default shots | 
**max_number_of_shots** | **int** | The maximum number of shots | 
**enabled** | **bool** | If it is enabled | 
**identifier** | **str** | The identifier of the backend | 
**protocol_version** | **int** |  | [optional] 

## Example

```python
from compute_api_client.models.backend_type import BackendType

# TODO update the JSON string below
json = "{}"
# create an instance of BackendType from a JSON string
backend_type_instance = BackendType.from_json(json)
# print the JSON string representation of the object
print(BackendType.to_json())

# convert the object into a dict
backend_type_dict = backend_type_instance.to_dict()
# create an instance of BackendType from a dict
backend_type_from_dict = BackendType.from_dict(backend_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


