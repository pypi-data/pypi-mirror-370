# compute_api_client.BackendTypesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**read_backend_type_backend_types_id_get**](BackendTypesApi.md#read_backend_type_backend_types_id_get) | **GET** /backend_types/{id} | Retrieve backend type
[**read_backend_types_backend_types_get**](BackendTypesApi.md#read_backend_types_backend_types_get) | **GET** /backend_types/ | List backend types
[**update_backend_type_backend_types_me_patch**](BackendTypesApi.md#update_backend_type_backend_types_me_patch) | **PATCH** /backend_types/me | Update backend type


# **read_backend_type_backend_types_id_get**
> BackendType read_backend_type_backend_types_id_get(id)

Retrieve backend type

Get backend type by ID.

### Example

* OAuth Authentication (user_bearer):
* Api Key Authentication (backend):

```python
import compute_api_client
from compute_api_client.models.backend_type import BackendType
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

# Configure API key authorization: backend
configuration.api_key['backend'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['backend'] = 'Bearer'

# Enter a context with an instance of the API client
async with compute_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = compute_api_client.BackendTypesApi(api_client)
    id = 56 # int | 

    try:
        # Retrieve backend type
        api_response = await api_instance.read_backend_type_backend_types_id_get(id)
        print("The response of BackendTypesApi->read_backend_type_backend_types_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BackendTypesApi->read_backend_type_backend_types_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**BackendType**](BackendType.md)

### Authorization

[user_bearer](../README.md#user_bearer), [backend](../README.md#backend)

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

# **read_backend_types_backend_types_get**
> PageBackendType read_backend_types_backend_types_get(id=id, name=name, infrastructure=infrastructure, description=description, image_id=image_id, is_hardware=is_hardware, supports_raw_data=supports_raw_data, nqubits=nqubits, status=status, default_number_of_shots=default_number_of_shots, max_number_of_shots=max_number_of_shots, enabled=enabled, identifier=identifier, protocol_version__isnull=protocol_version__isnull, protocol_version=protocol_version, sort_by=sort_by, latest=latest, page=page, size=size)

List backend types

Read backend types.

Only enabled backend types are returned.

### Example


```python
import compute_api_client
from compute_api_client.models.backend_status import BackendStatus
from compute_api_client.models.page_backend_type import PageBackendType
from compute_api_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = compute_api_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with compute_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = compute_api_client.BackendTypesApi(api_client)
    id = 56 # int |  (optional)
    name = 'name_example' # str |  (optional)
    infrastructure = 'infrastructure_example' # str |  (optional)
    description = 'description_example' # str |  (optional)
    image_id = 'image_id_example' # str |  (optional)
    is_hardware = True # bool |  (optional)
    supports_raw_data = True # bool |  (optional)
    nqubits = 56 # int |  (optional)
    status = compute_api_client.BackendStatus() # BackendStatus |  (optional)
    default_number_of_shots = 56 # int |  (optional)
    max_number_of_shots = 56 # int |  (optional)
    enabled = True # bool |  (optional)
    identifier = 'identifier_example' # str |  (optional)
    protocol_version__isnull = True # bool |  (optional)
    protocol_version = 56 # int |  (optional)
    sort_by = 'sort_by_example' # str | The field name to sort on. Prefix with '-' for descending order. E.g., '-created_on'. (optional)
    latest = True # bool | If True gets the most recently created object. (optional)
    page = 1 # int | Page number (optional) (default to 1)
    size = 50 # int | Page size (optional) (default to 50)

    try:
        # List backend types
        api_response = await api_instance.read_backend_types_backend_types_get(id=id, name=name, infrastructure=infrastructure, description=description, image_id=image_id, is_hardware=is_hardware, supports_raw_data=supports_raw_data, nqubits=nqubits, status=status, default_number_of_shots=default_number_of_shots, max_number_of_shots=max_number_of_shots, enabled=enabled, identifier=identifier, protocol_version__isnull=protocol_version__isnull, protocol_version=protocol_version, sort_by=sort_by, latest=latest, page=page, size=size)
        print("The response of BackendTypesApi->read_backend_types_backend_types_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BackendTypesApi->read_backend_types_backend_types_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | [optional] 
 **name** | **str**|  | [optional] 
 **infrastructure** | **str**|  | [optional] 
 **description** | **str**|  | [optional] 
 **image_id** | **str**|  | [optional] 
 **is_hardware** | **bool**|  | [optional] 
 **supports_raw_data** | **bool**|  | [optional] 
 **nqubits** | **int**|  | [optional] 
 **status** | [**BackendStatus**](.md)|  | [optional] 
 **default_number_of_shots** | **int**|  | [optional] 
 **max_number_of_shots** | **int**|  | [optional] 
 **enabled** | **bool**|  | [optional] 
 **identifier** | **str**|  | [optional] 
 **protocol_version__isnull** | **bool**|  | [optional] 
 **protocol_version** | **int**|  | [optional] 
 **sort_by** | **str**| The field name to sort on. Prefix with &#39;-&#39; for descending order. E.g., &#39;-created_on&#39;. | [optional] 
 **latest** | **bool**| If True gets the most recently created object. | [optional] 
 **page** | **int**| Page number | [optional] [default to 1]
 **size** | **int**| Page size | [optional] [default to 50]

### Return type

[**PageBackendType**](PageBackendType.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_backend_type_backend_types_me_patch**
> BackendType update_backend_type_backend_types_me_patch(backend_type_patch)

Update backend type

Update backend type by ID.

This endpoint allows for partial updates of backend type properties.

### Example

* Api Key Authentication (backend):

```python
import compute_api_client
from compute_api_client.models.backend_type import BackendType
from compute_api_client.models.backend_type_patch import BackendTypePatch
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
    api_instance = compute_api_client.BackendTypesApi(api_client)
    backend_type_patch = compute_api_client.BackendTypePatch() # BackendTypePatch | 

    try:
        # Update backend type
        api_response = await api_instance.update_backend_type_backend_types_me_patch(backend_type_patch)
        print("The response of BackendTypesApi->update_backend_type_backend_types_me_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BackendTypesApi->update_backend_type_backend_types_me_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **backend_type_patch** | [**BackendTypePatch**](BackendTypePatch.md)|  | 

### Return type

[**BackendType**](BackendType.md)

### Authorization

[backend](../README.md#backend)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Not Found |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

