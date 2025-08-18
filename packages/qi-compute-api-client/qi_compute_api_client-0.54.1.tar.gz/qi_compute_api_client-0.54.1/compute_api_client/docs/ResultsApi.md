# compute_api_client.ResultsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_result_results_post**](ResultsApi.md#create_result_results_post) | **POST** /results | Create result
[**delete_results_by_job_id_results_job_job_id_delete**](ResultsApi.md#delete_results_by_job_id_results_job_job_id_delete) | **DELETE** /results/job/{job_id} | Delete results by job ID
[**read_result_results_id_get**](ResultsApi.md#read_result_results_id_get) | **GET** /results/{id} | Retrieve result
[**read_results_by_algorithm_id_results_algorithm_algorithm_id_get**](ResultsApi.md#read_results_by_algorithm_id_results_algorithm_algorithm_id_get) | **GET** /results/algorithm/{algorithm_id} | Retrieve results by algorithm ID
[**read_results_by_job_id_results_job_job_id_get**](ResultsApi.md#read_results_by_job_id_results_job_job_id_get) | **GET** /results/job/{job_id} | Retrieve results by job ID


# **create_result_results_post**
> Result create_result_results_post(result_in)

Create result

Create new result.

### Example

* Api Key Authentication (backend):

```python
import compute_api_client
from compute_api_client.models.result import Result
from compute_api_client.models.result_in import ResultIn
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
    api_instance = compute_api_client.ResultsApi(api_client)
    result_in = compute_api_client.ResultIn() # ResultIn | 

    try:
        # Create result
        api_response = await api_instance.create_result_results_post(result_in)
        print("The response of ResultsApi->create_result_results_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ResultsApi->create_result_results_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **result_in** | [**ResultIn**](ResultIn.md)|  | 

### Return type

[**Result**](Result.md)

### Authorization

[backend](../README.md#backend)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_results_by_job_id_results_job_job_id_delete**
> delete_results_by_job_id_results_job_job_id_delete(job_id)

Delete results by job ID

Delete results by job ID.

### Example

* Api Key Authentication (backend):

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

# Configure API key authorization: backend
configuration.api_key['backend'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['backend'] = 'Bearer'

# Enter a context with an instance of the API client
async with compute_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = compute_api_client.ResultsApi(api_client)
    job_id = 56 # int | 

    try:
        # Delete results by job ID
        await api_instance.delete_results_by_job_id_results_job_job_id_delete(job_id)
    except Exception as e:
        print("Exception when calling ResultsApi->delete_results_by_job_id_results_job_job_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **int**|  | 

### Return type

void (empty response body)

### Authorization

[backend](../README.md#backend)

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

# **read_result_results_id_get**
> Result read_result_results_id_get(id)

Retrieve result

Get result by ID.

### Example

* OAuth Authentication (user_bearer):

```python
import compute_api_client
from compute_api_client.models.result import Result
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
    api_instance = compute_api_client.ResultsApi(api_client)
    id = 56 # int | 

    try:
        # Retrieve result
        api_response = await api_instance.read_result_results_id_get(id)
        print("The response of ResultsApi->read_result_results_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ResultsApi->read_result_results_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**Result**](Result.md)

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

# **read_results_by_algorithm_id_results_algorithm_algorithm_id_get**
> PageResult read_results_by_algorithm_id_results_algorithm_algorithm_id_get(algorithm_id, id=id, created_on=created_on, job_id=job_id, execution_time_in_seconds=execution_time_in_seconds, shots_requested__isnull=shots_requested__isnull, shots_requested=shots_requested, shots_done__isnull=shots_done__isnull, shots_done=shots_done, results__isnull=results__isnull, raw_data__isnull=raw_data__isnull, sort_by=sort_by, latest=latest, page=page, size=size)

Retrieve results by algorithm ID

Get results by algorithm ID.

### Example

* OAuth Authentication (user_bearer):

```python
import compute_api_client
from compute_api_client.models.page_result import PageResult
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
    api_instance = compute_api_client.ResultsApi(api_client)
    algorithm_id = 56 # int | 
    id = 56 # int |  (optional)
    created_on = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    job_id = 56 # int |  (optional)
    execution_time_in_seconds = 3.4 # float |  (optional)
    shots_requested__isnull = True # bool |  (optional)
    shots_requested = 56 # int |  (optional)
    shots_done__isnull = True # bool |  (optional)
    shots_done = 56 # int |  (optional)
    results__isnull = True # bool |  (optional)
    raw_data__isnull = True # bool |  (optional)
    sort_by = 'sort_by_example' # str | The field name to sort on. Prefix with '-' for descending order. E.g., '-created_on'. (optional)
    latest = True # bool | If True gets the most recently created object. (optional)
    page = 1 # int | Page number (optional) (default to 1)
    size = 50 # int | Page size (optional) (default to 50)

    try:
        # Retrieve results by algorithm ID
        api_response = await api_instance.read_results_by_algorithm_id_results_algorithm_algorithm_id_get(algorithm_id, id=id, created_on=created_on, job_id=job_id, execution_time_in_seconds=execution_time_in_seconds, shots_requested__isnull=shots_requested__isnull, shots_requested=shots_requested, shots_done__isnull=shots_done__isnull, shots_done=shots_done, results__isnull=results__isnull, raw_data__isnull=raw_data__isnull, sort_by=sort_by, latest=latest, page=page, size=size)
        print("The response of ResultsApi->read_results_by_algorithm_id_results_algorithm_algorithm_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ResultsApi->read_results_by_algorithm_id_results_algorithm_algorithm_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **algorithm_id** | **int**|  | 
 **id** | **int**|  | [optional] 
 **created_on** | **datetime**|  | [optional] 
 **job_id** | **int**|  | [optional] 
 **execution_time_in_seconds** | **float**|  | [optional] 
 **shots_requested__isnull** | **bool**|  | [optional] 
 **shots_requested** | **int**|  | [optional] 
 **shots_done__isnull** | **bool**|  | [optional] 
 **shots_done** | **int**|  | [optional] 
 **results__isnull** | **bool**|  | [optional] 
 **raw_data__isnull** | **bool**|  | [optional] 
 **sort_by** | **str**| The field name to sort on. Prefix with &#39;-&#39; for descending order. E.g., &#39;-created_on&#39;. | [optional] 
 **latest** | **bool**| If True gets the most recently created object. | [optional] 
 **page** | **int**| Page number | [optional] [default to 1]
 **size** | **int**| Page size | [optional] [default to 50]

### Return type

[**PageResult**](PageResult.md)

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

# **read_results_by_job_id_results_job_job_id_get**
> PageResult read_results_by_job_id_results_job_job_id_get(job_id, page=page, size=size, sort_by=sort_by, latest=latest)

Retrieve results by job ID

Get results by job ID.

### Example

* OAuth Authentication (user_bearer):

```python
import compute_api_client
from compute_api_client.models.page_result import PageResult
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
    api_instance = compute_api_client.ResultsApi(api_client)
    job_id = 56 # int | 
    page = 1 # int | Page number (optional) (default to 1)
    size = 50 # int | Page size (optional) (default to 50)
    sort_by = 'sort_by_example' # str |  (optional)
    latest = True # bool |  (optional)

    try:
        # Retrieve results by job ID
        api_response = await api_instance.read_results_by_job_id_results_job_job_id_get(job_id, page=page, size=size, sort_by=sort_by, latest=latest)
        print("The response of ResultsApi->read_results_by_job_id_results_job_job_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ResultsApi->read_results_by_job_id_results_job_job_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **int**|  | 
 **page** | **int**| Page number | [optional] [default to 1]
 **size** | **int**| Page size | [optional] [default to 50]
 **sort_by** | **str**|  | [optional] 
 **latest** | **bool**|  | [optional] 

### Return type

[**PageResult**](PageResult.md)

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

