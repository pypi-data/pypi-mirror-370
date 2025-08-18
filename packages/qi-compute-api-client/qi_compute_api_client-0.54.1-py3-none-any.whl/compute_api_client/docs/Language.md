# Language


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | The ID of the language | 
**name** | **str** | Name of the language | 
**version** | **str** | Version of the language | 

## Example

```python
from compute_api_client.models.language import Language

# TODO update the JSON string below
json = "{}"
# create an instance of Language from a JSON string
language_instance = Language.from_json(json)
# print the JSON string representation of the object
print(Language.to_json())

# convert the object into a dict
language_dict = language_instance.to_dict()
# create an instance of Language from a dict
language_from_dict = Language.from_dict(language_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


