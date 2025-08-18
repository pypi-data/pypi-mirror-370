# compute_api_client.FinalResultsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_final_result_final_results_post**](FinalResultsApi.md#create_final_result_final_results_post) | **POST** /final_results | Create final result
[**read_final_result_by_job_id_final_results_job_job_id_get**](FinalResultsApi.md#read_final_result_by_job_id_final_results_job_job_id_get) | **GET** /final_results/job/{job_id} | Retrieve final result by job ID
[**read_final_result_final_results_id_get**](FinalResultsApi.md#read_final_result_final_results_id_get) | **GET** /final_results/{id} | Retrieve final result


# **create_final_result_final_results_post**
> FinalResult create_final_result_final_results_post(final_result_in)

Create final result

Create new final result.

### Example

* OAuth Authentication (user_bearer):
* Api Key Authentication (backend):

```python
import compute_api_client
from compute_api_client.models.final_result import FinalResult
from compute_api_client.models.final_result_in import FinalResultIn
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
    api_instance = compute_api_client.FinalResultsApi(api_client)
    final_result_in = compute_api_client.FinalResultIn() # FinalResultIn | 

    try:
        # Create final result
        api_response = await api_instance.create_final_result_final_results_post(final_result_in)
        print("The response of FinalResultsApi->create_final_result_final_results_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FinalResultsApi->create_final_result_final_results_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **final_result_in** | [**FinalResultIn**](FinalResultIn.md)|  | 

### Return type

[**FinalResult**](FinalResult.md)

### Authorization

[user_bearer](../README.md#user_bearer), [backend](../README.md#backend)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **read_final_result_by_job_id_final_results_job_job_id_get**
> FinalResult read_final_result_by_job_id_final_results_job_job_id_get(job_id)

Retrieve final result by job ID

Get final result by job ID.

### Example

* OAuth Authentication (user_bearer):

```python
import compute_api_client
from compute_api_client.models.final_result import FinalResult
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
    api_instance = compute_api_client.FinalResultsApi(api_client)
    job_id = 56 # int | 

    try:
        # Retrieve final result by job ID
        api_response = await api_instance.read_final_result_by_job_id_final_results_job_job_id_get(job_id)
        print("The response of FinalResultsApi->read_final_result_by_job_id_final_results_job_job_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FinalResultsApi->read_final_result_by_job_id_final_results_job_job_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **int**|  | 

### Return type

[**FinalResult**](FinalResult.md)

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

# **read_final_result_final_results_id_get**
> FinalResult read_final_result_final_results_id_get(id)

Retrieve final result

Get final result by ID.

### Example

* OAuth Authentication (user_bearer):

```python
import compute_api_client
from compute_api_client.models.final_result import FinalResult
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
    api_instance = compute_api_client.FinalResultsApi(api_client)
    id = 56 # int | 

    try:
        # Retrieve final result
        api_response = await api_instance.read_final_result_final_results_id_get(id)
        print("The response of FinalResultsApi->read_final_result_final_results_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FinalResultsApi->read_final_result_final_results_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**FinalResult**](FinalResult.md)

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

