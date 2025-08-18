# PageLanguage


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[Language]**](Language.md) |  | 
**total** | **int** |  | [optional] 
**page** | **int** |  | 
**size** | **int** |  | 
**pages** | **int** |  | [optional] 

## Example

```python
from compute_api_client.models.page_language import PageLanguage

# TODO update the JSON string below
json = "{}"
# create an instance of PageLanguage from a JSON string
page_language_instance = PageLanguage.from_json(json)
# print the JSON string representation of the object
print(PageLanguage.to_json())

# convert the object into a dict
page_language_dict = page_language_instance.to_dict()
# create an instance of PageLanguage from a dict
page_language_from_dict = PageLanguage.from_dict(page_language_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


