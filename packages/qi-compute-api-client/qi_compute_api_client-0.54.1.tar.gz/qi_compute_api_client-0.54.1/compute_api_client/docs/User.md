# User


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | The id of the user | 
**full_name** | **str** | The full name of the user | 
**email** | **str** | The email id of the user | 
**is_superuser** | **bool** | If the user is superuser | 
**is_staff** | **bool** | If the user is staff | 
**is_active** | **bool** | If the user is active | 
**is_confirmed** | **bool** | If the user is confirmed | 
**oidc_sub** | **str** | User identifier from OIDC provider | 

## Example

```python
from compute_api_client.models.user import User

# TODO update the JSON string below
json = "{}"
# create an instance of User from a JSON string
user_instance = User.from_json(json)
# print the JSON string representation of the object
print(User.to_json())

# convert the object into a dict
user_dict = user_instance.to_dict()
# create an instance of User from a dict
user_from_dict = User.from_dict(user_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


