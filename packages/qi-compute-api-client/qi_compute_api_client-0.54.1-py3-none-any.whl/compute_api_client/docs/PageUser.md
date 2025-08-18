# PageUser


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[User]**](User.md) |  | 
**total** | **int** |  | [optional] 
**page** | **int** |  | 
**size** | **int** |  | 
**pages** | **int** |  | [optional] 

## Example

```python
from compute_api_client.models.page_user import PageUser

# TODO update the JSON string below
json = "{}"
# create an instance of PageUser from a JSON string
page_user_instance = PageUser.from_json(json)
# print the JSON string representation of the object
print(PageUser.to_json())

# convert the object into a dict
page_user_dict = page_user_instance.to_dict()
# create an instance of PageUser from a dict
page_user_from_dict = PageUser.from_dict(page_user_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


