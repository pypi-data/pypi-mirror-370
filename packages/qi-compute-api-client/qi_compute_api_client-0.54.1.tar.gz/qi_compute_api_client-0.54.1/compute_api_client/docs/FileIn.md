# FileIn


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**commit_id** | **int** | ID of the commit | 
**content** | **str** | The content of the file | 
**language_id** | **int** | ID of the language | 
**compile_stage** | [**CompileStage**](CompileStage.md) | Stage upto which the file has been compiled | 
**compile_properties** | **Dict[str, object]** | The compile properties of the file | 
**generated** | **bool** | If the file is a generated file | [optional] [default to False]
**name** | **str** |  | [optional] 

## Example

```python
from compute_api_client.models.file_in import FileIn

# TODO update the JSON string below
json = "{}"
# create an instance of FileIn from a JSON string
file_in_instance = FileIn.from_json(json)
# print the JSON string representation of the object
print(FileIn.to_json())

# convert the object into a dict
file_in_dict = file_in_instance.to_dict()
# create an instance of FileIn from a dict
file_in_from_dict = FileIn.from_dict(file_in_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


