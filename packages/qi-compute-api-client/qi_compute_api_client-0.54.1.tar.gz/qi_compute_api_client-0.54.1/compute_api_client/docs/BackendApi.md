# compute_api_client.BackendApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_backend_backends_post**](BackendApi.md#create_backend_backends_post) | **POST** /backends | Create backend
[**read_backend_backends_id_get**](BackendApi.md#read_backend_backends_id_get) | **GET** /backends/{id} | Retrieve backend
[**read_backend_self_backends_me_get**](BackendApi.md#read_backend_self_backends_me_get) | **GET** /backends/me | Retrieve backend
[**read_backends_backends_get**](BackendApi.md#read_backends_backends_get) | **GET** /backends | List backends
[**update_backend_self_backends_me_patch**](BackendApi.md#update_backend_self_backends_me_patch) | **PATCH** /backends/me | Update backend


# **create_backend_backends_post**
> BackendWithAuthentication create_backend_backends_post(backend_in)

Create backend

Create new backend.

### Example

* OAuth Authentication (user_bearer):

```python
import compute_api_client
from compute_api_client.models.backend_in import BackendIn
from compute_api_client.models.backend_with_authentication import BackendWithAuthentication
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
    api_instance = compute_api_client.BackendApi(api_client)
    backend_in = compute_api_client.BackendIn() # BackendIn | 

    try:
        # Create backend
        api_response = await api_instance.create_backend_backends_post(backend_in)
        print("The response of BackendApi->create_backend_backends_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BackendApi->create_backend_backends_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **backend_in** | [**BackendIn**](BackendIn.md)|  | 

### Return type

[**BackendWithAuthentication**](BackendWithAuthentication.md)

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

# **read_backend_backends_id_get**
> Backend read_backend_backends_id_get(id)

Retrieve backend

Get backend by ID.

### Example

* OAuth Authentication (user_bearer):

```python
import compute_api_client
from compute_api_client.models.backend import Backend
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
    api_instance = compute_api_client.BackendApi(api_client)
    id = 56 # int | 

    try:
        # Retrieve backend
        api_response = await api_instance.read_backend_backends_id_get(id)
        print("The response of BackendApi->read_backend_backends_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BackendApi->read_backend_backends_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**Backend**](Backend.md)

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

# **read_backend_self_backends_me_get**
> Backend read_backend_self_backends_me_get()

Retrieve backend

Read backend.

### Example

* Api Key Authentication (backend):

```python
import compute_api_client
from compute_api_client.models.backend import Backend
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

# Configure API key authorization: backend
configuration.api_key['backend'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['backend'] = 'Bearer'

# Enter a context with an instance of the API client
async with compute_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = compute_api_client.BackendApi(api_client)

    try:
        # Retrieve backend
        api_response = await api_instance.read_backend_self_backends_me_get()
        print("The response of BackendApi->read_backend_self_backends_me_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BackendApi->read_backend_self_backends_me_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**Backend**](Backend.md)

### Authorization

[backend](../README.md#backend)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **read_backends_backends_get**
> PageBackend read_backends_backends_get(id=id, name=name, location=location, backend_type_id=backend_type_id, status=status, last_heartbeat=last_heartbeat, sort_by=sort_by, latest=latest, page=page, size=size)

List backends

Read backends.

### Example

* OAuth Authentication (user_bearer):

```python
import compute_api_client
from compute_api_client.models.backend_status import BackendStatus
from compute_api_client.models.page_backend import PageBackend
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
    api_instance = compute_api_client.BackendApi(api_client)
    id = 56 # int |  (optional)
    name = 'name_example' # str |  (optional)
    location = 'location_example' # str |  (optional)
    backend_type_id = 56 # int |  (optional)
    status = compute_api_client.BackendStatus() # BackendStatus |  (optional)
    last_heartbeat = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    sort_by = 'sort_by_example' # str | The field name to sort on. Prefix with '-' for descending order. E.g., '-created_on'. (optional)
    latest = True # bool | If True gets the most recently created object. (optional)
    page = 1 # int | Page number (optional) (default to 1)
    size = 50 # int | Page size (optional) (default to 50)

    try:
        # List backends
        api_response = await api_instance.read_backends_backends_get(id=id, name=name, location=location, backend_type_id=backend_type_id, status=status, last_heartbeat=last_heartbeat, sort_by=sort_by, latest=latest, page=page, size=size)
        print("The response of BackendApi->read_backends_backends_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BackendApi->read_backends_backends_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | [optional] 
 **name** | **str**|  | [optional] 
 **location** | **str**|  | [optional] 
 **backend_type_id** | **int**|  | [optional] 
 **status** | [**BackendStatus**](.md)|  | [optional] 
 **last_heartbeat** | **datetime**|  | [optional] 
 **sort_by** | **str**| The field name to sort on. Prefix with &#39;-&#39; for descending order. E.g., &#39;-created_on&#39;. | [optional] 
 **latest** | **bool**| If True gets the most recently created object. | [optional] 
 **page** | **int**| Page number | [optional] [default to 1]
 **size** | **int**| Page size | [optional] [default to 50]

### Return type

[**PageBackend**](PageBackend.md)

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

# **update_backend_self_backends_me_patch**
> Backend update_backend_self_backends_me_patch(backend_patch)

Update backend

Update backend.

### Example

* Api Key Authentication (backend):

```python
import compute_api_client
from compute_api_client.models.backend import Backend
from compute_api_client.models.backend_patch import BackendPatch
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

# Configure API key authorization: backend
configuration.api_key['backend'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['backend'] = 'Bearer'

# Enter a context with an instance of the API client
async with compute_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = compute_api_client.BackendApi(api_client)
    backend_patch = compute_api_client.BackendPatch() # BackendPatch | 

    try:
        # Update backend
        api_response = await api_instance.update_backend_self_backends_me_patch(backend_patch)
        print("The response of BackendApi->update_backend_self_backends_me_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BackendApi->update_backend_self_backends_me_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **backend_patch** | [**BackendPatch**](BackendPatch.md)|  | 

### Return type

[**Backend**](Backend.md)

### Authorization

[backend](../README.md#backend)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

