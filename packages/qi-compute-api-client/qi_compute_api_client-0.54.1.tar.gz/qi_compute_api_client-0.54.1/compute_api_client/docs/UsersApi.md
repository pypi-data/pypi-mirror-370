# compute_api_client.UsersApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_user_users_post**](UsersApi.md#create_user_users_post) | **POST** /users | Create user
[**delete_user_users_id_delete**](UsersApi.md#delete_user_users_id_delete) | **DELETE** /users/{id} | Destroy user
[**read_user_users_id_get**](UsersApi.md#read_user_users_id_get) | **GET** /users/{id} | Retrieve user
[**read_users_users_get**](UsersApi.md#read_users_users_get) | **GET** /users | List users


# **create_user_users_post**
> User create_user_users_post(user_in)

Create user

Create new user.

### Example

* OAuth Authentication (user_bearer):

```python
import compute_api_client
from compute_api_client.models.user import User
from compute_api_client.models.user_in import UserIn
from compute_api_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = compute_api_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
async with compute_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = compute_api_client.UsersApi(api_client)
    user_in = compute_api_client.UserIn() # UserIn | 

    try:
        # Create user
        api_response = await api_instance.create_user_users_post(user_in)
        print("The response of UsersApi->create_user_users_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsersApi->create_user_users_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_in** | [**UserIn**](UserIn.md)|  | 

### Return type

[**User**](User.md)

### Authorization

[user_bearer](../README.md#user_bearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_user_users_id_delete**
> delete_user_users_id_delete(id)

Destroy user

Delete a user.

### Example

* OAuth Authentication (user_bearer):

```python
import compute_api_client
from compute_api_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = compute_api_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
async with compute_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = compute_api_client.UsersApi(api_client)
    id = 56 # int | 

    try:
        # Destroy user
        await api_instance.delete_user_users_id_delete(id)
    except Exception as e:
        print("Exception when calling UsersApi->delete_user_users_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

void (empty response body)

### Authorization

[user_bearer](../README.md#user_bearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**404** | Not Found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **read_user_users_id_get**
> User read_user_users_id_get(id)

Retrieve user

Get user by ID.

### Example

* OAuth Authentication (user_bearer):

```python
import compute_api_client
from compute_api_client.models.user import User
from compute_api_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = compute_api_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
async with compute_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = compute_api_client.UsersApi(api_client)
    id = 56 # int | 

    try:
        # Retrieve user
        api_response = await api_instance.read_user_users_id_get(id)
        print("The response of UsersApi->read_user_users_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsersApi->read_user_users_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**User**](User.md)

### Authorization

[user_bearer](../README.md#user_bearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Not Found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **read_users_users_get**
> PageUser read_users_users_get(id=id, full_name=full_name, email=email, is_superuser=is_superuser, is_staff=is_staff, is_active=is_active, is_confirmed=is_confirmed, oidc_sub=oidc_sub, sort_by=sort_by, latest=latest, page=page, size=size)

List users

Read users.

### Example

* OAuth Authentication (user_bearer):

```python
import compute_api_client
from compute_api_client.models.page_user import PageUser
from compute_api_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = compute_api_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
async with compute_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = compute_api_client.UsersApi(api_client)
    id = 56 # int |  (optional)
    full_name = 'full_name_example' # str |  (optional)
    email = 'email_example' # str |  (optional)
    is_superuser = True # bool |  (optional)
    is_staff = True # bool |  (optional)
    is_active = True # bool |  (optional)
    is_confirmed = True # bool |  (optional)
    oidc_sub = 'oidc_sub_example' # str |  (optional)
    sort_by = 'sort_by_example' # str | The field name to sort on. Prefix with '-' for descending order. E.g., '-created_on'. (optional)
    latest = True # bool | If True gets the most recently created object. (optional)
    page = 1 # int | Page number (optional) (default to 1)
    size = 50 # int | Page size (optional) (default to 50)

    try:
        # List users
        api_response = await api_instance.read_users_users_get(id=id, full_name=full_name, email=email, is_superuser=is_superuser, is_staff=is_staff, is_active=is_active, is_confirmed=is_confirmed, oidc_sub=oidc_sub, sort_by=sort_by, latest=latest, page=page, size=size)
        print("The response of UsersApi->read_users_users_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsersApi->read_users_users_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | [optional] 
 **full_name** | **str**|  | [optional] 
 **email** | **str**|  | [optional] 
 **is_superuser** | **bool**|  | [optional] 
 **is_staff** | **bool**|  | [optional] 
 **is_active** | **bool**|  | [optional] 
 **is_confirmed** | **bool**|  | [optional] 
 **oidc_sub** | **str**|  | [optional] 
 **sort_by** | **str**| The field name to sort on. Prefix with &#39;-&#39; for descending order. E.g., &#39;-created_on&#39;. | [optional] 
 **latest** | **bool**| If True gets the most recently created object. | [optional] 
 **page** | **int**| Page number | [optional] [default to 1]
 **size** | **int**| Page size | [optional] [default to 50]

### Return type

[**PageUser**](PageUser.md)

### Authorization

[user_bearer](../README.md#user_bearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

