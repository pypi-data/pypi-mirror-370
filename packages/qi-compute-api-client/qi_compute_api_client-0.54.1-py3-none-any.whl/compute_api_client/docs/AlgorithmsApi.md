# compute_api_client.AlgorithmsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_algorithm_algorithms_post**](AlgorithmsApi.md#create_algorithm_algorithms_post) | **POST** /algorithms | Create algorithm
[**delete_algorithm_algorithms_id_delete**](AlgorithmsApi.md#delete_algorithm_algorithms_id_delete) | **DELETE** /algorithms/{id} | Destroy algorithm
[**read_algorithm_algorithms_id_get**](AlgorithmsApi.md#read_algorithm_algorithms_id_get) | **GET** /algorithms/{id} | Retrieve algorithm
[**read_algorithms_algorithms_get**](AlgorithmsApi.md#read_algorithms_algorithms_get) | **GET** /algorithms | List algorithms
[**update_algorithm_algorithms_id_put**](AlgorithmsApi.md#update_algorithm_algorithms_id_put) | **PUT** /algorithms/{id} | Update algorithm


# **create_algorithm_algorithms_post**
> Algorithm create_algorithm_algorithms_post(algorithm_in)

Create algorithm

Create new algorithm.

### Example

* OAuth Authentication (user_bearer):

```python
import compute_api_client
from compute_api_client.models.algorithm import Algorithm
from compute_api_client.models.algorithm_in import AlgorithmIn
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
    api_instance = compute_api_client.AlgorithmsApi(api_client)
    algorithm_in = compute_api_client.AlgorithmIn() # AlgorithmIn | 

    try:
        # Create algorithm
        api_response = await api_instance.create_algorithm_algorithms_post(algorithm_in)
        print("The response of AlgorithmsApi->create_algorithm_algorithms_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AlgorithmsApi->create_algorithm_algorithms_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **algorithm_in** | [**AlgorithmIn**](AlgorithmIn.md)|  | 

### Return type

[**Algorithm**](Algorithm.md)

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

# **delete_algorithm_algorithms_id_delete**
> delete_algorithm_algorithms_id_delete(id)

Destroy algorithm

Delete an algorithm.

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
    api_instance = compute_api_client.AlgorithmsApi(api_client)
    id = 56 # int | 

    try:
        # Destroy algorithm
        await api_instance.delete_algorithm_algorithms_id_delete(id)
    except Exception as e:
        print("Exception when calling AlgorithmsApi->delete_algorithm_algorithms_id_delete: %s\n" % e)
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

# **read_algorithm_algorithms_id_get**
> Algorithm read_algorithm_algorithms_id_get(id)

Retrieve algorithm

Get algorithm by ID.

### Example

* OAuth Authentication (user_bearer):
* Api Key Authentication (backend):

```python
import compute_api_client
from compute_api_client.models.algorithm import Algorithm
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
    api_instance = compute_api_client.AlgorithmsApi(api_client)
    id = 56 # int | 

    try:
        # Retrieve algorithm
        api_response = await api_instance.read_algorithm_algorithms_id_get(id)
        print("The response of AlgorithmsApi->read_algorithm_algorithms_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AlgorithmsApi->read_algorithm_algorithms_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**Algorithm**](Algorithm.md)

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

# **read_algorithms_algorithms_get**
> PageAlgorithm read_algorithms_algorithms_get(search=search, id=id, project_id=project_id, type=type, shared=shared, link__isnull=link__isnull, link=link, name=name, sort_by=sort_by, latest=latest, page=page, size=size)

List algorithms

List algorithms.

### Example

* OAuth Authentication (user_bearer):

```python
import compute_api_client
from compute_api_client.models.algorithm_type import AlgorithmType
from compute_api_client.models.page_algorithm import PageAlgorithm
from compute_api_client.models.share_type import ShareType
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
    api_instance = compute_api_client.AlgorithmsApi(api_client)
    search = 'search_example' # str | Substring search for algorithm names (optional)
    id = 56 # int |  (optional)
    project_id = 56 # int |  (optional)
    type = compute_api_client.AlgorithmType() # AlgorithmType |  (optional)
    shared = compute_api_client.ShareType() # ShareType |  (optional)
    link__isnull = True # bool |  (optional)
    link = 'link_example' # str |  (optional)
    name = 'name_example' # str |  (optional)
    sort_by = 'sort_by_example' # str | The field name to sort on. Prefix with '-' for descending order. E.g., '-created_on'. (optional)
    latest = True # bool | If True gets the most recently created object. (optional)
    page = 1 # int | Page number (optional) (default to 1)
    size = 50 # int | Page size (optional) (default to 50)

    try:
        # List algorithms
        api_response = await api_instance.read_algorithms_algorithms_get(search=search, id=id, project_id=project_id, type=type, shared=shared, link__isnull=link__isnull, link=link, name=name, sort_by=sort_by, latest=latest, page=page, size=size)
        print("The response of AlgorithmsApi->read_algorithms_algorithms_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AlgorithmsApi->read_algorithms_algorithms_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **search** | **str**| Substring search for algorithm names | [optional] 
 **id** | **int**|  | [optional] 
 **project_id** | **int**|  | [optional] 
 **type** | [**AlgorithmType**](.md)|  | [optional] 
 **shared** | [**ShareType**](.md)|  | [optional] 
 **link__isnull** | **bool**|  | [optional] 
 **link** | **str**|  | [optional] 
 **name** | **str**|  | [optional] 
 **sort_by** | **str**| The field name to sort on. Prefix with &#39;-&#39; for descending order. E.g., &#39;-created_on&#39;. | [optional] 
 **latest** | **bool**| If True gets the most recently created object. | [optional] 
 **page** | **int**| Page number | [optional] [default to 1]
 **size** | **int**| Page size | [optional] [default to 50]

### Return type

[**PageAlgorithm**](PageAlgorithm.md)

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

# **update_algorithm_algorithms_id_put**
> Algorithm update_algorithm_algorithms_id_put(id, algorithm_in)

Update algorithm

Update an algorithm.

### Example

* OAuth Authentication (user_bearer):

```python
import compute_api_client
from compute_api_client.models.algorithm import Algorithm
from compute_api_client.models.algorithm_in import AlgorithmIn
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
    api_instance = compute_api_client.AlgorithmsApi(api_client)
    id = 56 # int | 
    algorithm_in = compute_api_client.AlgorithmIn() # AlgorithmIn | 

    try:
        # Update algorithm
        api_response = await api_instance.update_algorithm_algorithms_id_put(id, algorithm_in)
        print("The response of AlgorithmsApi->update_algorithm_algorithms_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AlgorithmsApi->update_algorithm_algorithms_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **algorithm_in** | [**AlgorithmIn**](AlgorithmIn.md)|  | 

### Return type

[**Algorithm**](Algorithm.md)

### Authorization

[user_bearer](../README.md#user_bearer)

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

