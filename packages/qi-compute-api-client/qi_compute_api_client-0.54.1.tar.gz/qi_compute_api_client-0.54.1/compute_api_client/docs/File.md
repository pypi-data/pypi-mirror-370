# File


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | ID of the file | 
**commit_id** | **int** | ID of the commit | 
**content** | **str** | The content of the file | 
**language_id** | **int** | ID of the language | 
**compile_stage** | [**CompileStage**](CompileStage.md) | The stage upto which the file has been compiled | 
**compile_properties** | **Dict[str, object]** | The compile properties of the file | 
**generated** | **bool** | If the file is a generated file | 
**name** | **str** |  | [optional] 

## Example

```python
from compute_api_client.models.file import File

# TODO update the JSON string below
json = "{}"
# create an instance of File from a JSON string
file_instance = File.from_json(json)
# print the JSON string representation of the object
print(File.to_json())

# convert the object into a dict
file_dict = file_instance.to_dict()
# create an instance of File from a dict
file_from_dict = File.from_dict(file_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


