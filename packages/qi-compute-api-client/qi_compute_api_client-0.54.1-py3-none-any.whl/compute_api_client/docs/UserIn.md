# UserIn


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**full_name** | **str** | The full name of the user | 
**email** | **str** | The email id of the user | 
**is_superuser** | **bool** | If the user is superuser | [optional] [default to False]
**is_staff** | **bool** | If the user is staff | [optional] [default to False]
**is_active** | **bool** | If the user is active | [optional] [default to False]
**is_confirmed** | **bool** | If the user is confirmed | [optional] [default to False]
**oidc_sub** | **str** | User identifier from OIDC provider | 

## Example

```python
from compute_api_client.models.user_in import UserIn

# TODO update the JSON string below
json = "{}"
# create an instance of UserIn from a JSON string
user_in_instance = UserIn.from_json(json)
# print the JSON string representation of the object
print(UserIn.to_json())

# convert the object into a dict
user_in_dict = user_in_instance.to_dict()
# create an instance of UserIn from a dict
user_in_from_dict = UserIn.from_dict(user_in_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


