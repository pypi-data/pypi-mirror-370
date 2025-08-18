# PageMember


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[Member]**](Member.md) |  | 
**total** | **int** |  | [optional] 
**page** | **int** |  | 
**size** | **int** |  | 
**pages** | **int** |  | [optional] 

## Example

```python
from compute_api_client.models.page_member import PageMember

# TODO update the JSON string below
json = "{}"
# create an instance of PageMember from a JSON string
page_member_instance = PageMember.from_json(json)
# print the JSON string representation of the object
print(PageMember.to_json())

# convert the object into a dict
page_member_dict = page_member_instance.to_dict()
# create an instance of PageMember from a dict
page_member_from_dict = PageMember.from_dict(page_member_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


