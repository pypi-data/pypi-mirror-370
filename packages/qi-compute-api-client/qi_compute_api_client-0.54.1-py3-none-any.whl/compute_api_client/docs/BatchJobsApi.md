# compute_api_client.BatchJobsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_batch_job_batch_jobs_post**](BatchJobsApi.md#create_batch_job_batch_jobs_post) | **POST** /batch_jobs | Create batch job
[**enqueue_batch_job_batch_jobs_id_enqueue_patch**](BatchJobsApi.md#enqueue_batch_job_batch_jobs_id_enqueue_patch) | **PATCH** /batch_jobs/{id}/enqueue | Enqueue batch job for execution
[**finish_batch_job_batch_jobs_id_finish_patch**](BatchJobsApi.md#finish_batch_job_batch_jobs_id_finish_patch) | **PATCH** /batch_jobs/{id}/finish | Finish batch job
[**peek_batch_job_batch_jobs_peek_patch**](BatchJobsApi.md#peek_batch_job_batch_jobs_peek_patch) | **PATCH** /batch_jobs/peek | Peek batch job
[**pop_batch_job_batch_jobs_pop_patch**](BatchJobsApi.md#pop_batch_job_batch_jobs_pop_patch) | **PATCH** /batch_jobs/pop | Take batch job
[**read_batch_jobs_batch_jobs_get**](BatchJobsApi.md#read_batch_jobs_batch_jobs_get) | **GET** /batch_jobs | List batch jobs
[**unpop_batch_job_batch_jobs_id_unpop_patch**](BatchJobsApi.md#unpop_batch_job_batch_jobs_id_unpop_patch) | **PATCH** /batch_jobs/{id}/unpop | Take batch job


# **create_batch_job_batch_jobs_post**
> BatchJob create_batch_job_batch_jobs_post(batch_job_in)

Create batch job

Create new batch job.

### Example

* OAuth Authentication (user_bearer):

```python
import compute_api_client
from compute_api_client.models.batch_job import BatchJob
from compute_api_client.models.batch_job_in import BatchJobIn
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
    api_instance = compute_api_client.BatchJobsApi(api_client)
    batch_job_in = compute_api_client.BatchJobIn() # BatchJobIn | 

    try:
        # Create batch job
        api_response = await api_instance.create_batch_job_batch_jobs_post(batch_job_in)
        print("The response of BatchJobsApi->create_batch_job_batch_jobs_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BatchJobsApi->create_batch_job_batch_jobs_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **batch_job_in** | [**BatchJobIn**](BatchJobIn.md)|  | 

### Return type

[**BatchJob**](BatchJob.md)

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

# **enqueue_batch_job_batch_jobs_id_enqueue_patch**
> BatchJob enqueue_batch_job_batch_jobs_id_enqueue_patch(id)

Enqueue batch job for execution

Enqueue batch job for execution.

### Example

* OAuth Authentication (user_bearer):

```python
import compute_api_client
from compute_api_client.models.batch_job import BatchJob
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
    api_instance = compute_api_client.BatchJobsApi(api_client)
    id = 56 # int | 

    try:
        # Enqueue batch job for execution
        api_response = await api_instance.enqueue_batch_job_batch_jobs_id_enqueue_patch(id)
        print("The response of BatchJobsApi->enqueue_batch_job_batch_jobs_id_enqueue_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BatchJobsApi->enqueue_batch_job_batch_jobs_id_enqueue_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**BatchJob**](BatchJob.md)

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

# **finish_batch_job_batch_jobs_id_finish_patch**
> BatchJob finish_batch_job_batch_jobs_id_finish_patch(id)

Finish batch job

Finish batch job.

### Example

* OAuth Authentication (user_bearer):
* Api Key Authentication (backend):

```python
import compute_api_client
from compute_api_client.models.batch_job import BatchJob
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
    api_instance = compute_api_client.BatchJobsApi(api_client)
    id = 56 # int | 

    try:
        # Finish batch job
        api_response = await api_instance.finish_batch_job_batch_jobs_id_finish_patch(id)
        print("The response of BatchJobsApi->finish_batch_job_batch_jobs_id_finish_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BatchJobsApi->finish_batch_job_batch_jobs_id_finish_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**BatchJob**](BatchJob.md)

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

# **peek_batch_job_batch_jobs_peek_patch**
> BatchJob peek_batch_job_batch_jobs_peek_patch(request_body)

Peek batch job

Get batch job that can be taken up, excluding list of IDs.

### Example

* Api Key Authentication (backend):

```python
import compute_api_client
from compute_api_client.models.batch_job import BatchJob
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
    api_instance = compute_api_client.BatchJobsApi(api_client)
    request_body = [56] # List[Optional[int]] | 

    try:
        # Peek batch job
        api_response = await api_instance.peek_batch_job_batch_jobs_peek_patch(request_body)
        print("The response of BatchJobsApi->peek_batch_job_batch_jobs_peek_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BatchJobsApi->peek_batch_job_batch_jobs_peek_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | [**List[Optional[int]]**](int.md)|  | 

### Return type

[**BatchJob**](BatchJob.md)

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

# **pop_batch_job_batch_jobs_pop_patch**
> BatchJob pop_batch_job_batch_jobs_pop_patch()

Take batch job

Claim batch job.

### Example

* Api Key Authentication (backend):

```python
import compute_api_client
from compute_api_client.models.batch_job import BatchJob
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
    api_instance = compute_api_client.BatchJobsApi(api_client)

    try:
        # Take batch job
        api_response = await api_instance.pop_batch_job_batch_jobs_pop_patch()
        print("The response of BatchJobsApi->pop_batch_job_batch_jobs_pop_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BatchJobsApi->pop_batch_job_batch_jobs_pop_patch: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**BatchJob**](BatchJob.md)

### Authorization

[backend](../README.md#backend)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**404** | Not Found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **read_batch_jobs_batch_jobs_get**
> PageBatchJob read_batch_jobs_batch_jobs_get(id=id, created_on=created_on, status=status, backend_type_id=backend_type_id, backend_id__isnull=backend_id__isnull, backend_id=backend_id, queued_at__isnull=queued_at__isnull, queued_at=queued_at, reserved_at__isnull=reserved_at__isnull, reserved_at=reserved_at, finished_at__isnull=finished_at__isnull, finished_at=finished_at, aggregated_algorithm_type=aggregated_algorithm_type, sort_by=sort_by, latest=latest, page=page, size=size)

List batch jobs

List batch jobs.

### Example

* OAuth Authentication (user_bearer):

```python
import compute_api_client
from compute_api_client.models.algorithm_type import AlgorithmType
from compute_api_client.models.batch_job_status import BatchJobStatus
from compute_api_client.models.page_batch_job import PageBatchJob
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
    api_instance = compute_api_client.BatchJobsApi(api_client)
    id = 56 # int |  (optional)
    created_on = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    status = compute_api_client.BatchJobStatus() # BatchJobStatus |  (optional)
    backend_type_id = 56 # int |  (optional)
    backend_id__isnull = True # bool |  (optional)
    backend_id = 56 # int |  (optional)
    queued_at__isnull = True # bool |  (optional)
    queued_at = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    reserved_at__isnull = True # bool |  (optional)
    reserved_at = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    finished_at__isnull = True # bool |  (optional)
    finished_at = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    aggregated_algorithm_type = compute_api_client.AlgorithmType() # AlgorithmType |  (optional)
    sort_by = 'sort_by_example' # str | The field name to sort on. Prefix with '-' for descending order. E.g., '-created_on'. (optional)
    latest = True # bool | If True gets the most recently created object. (optional)
    page = 1 # int | Page number (optional) (default to 1)
    size = 50 # int | Page size (optional) (default to 50)

    try:
        # List batch jobs
        api_response = await api_instance.read_batch_jobs_batch_jobs_get(id=id, created_on=created_on, status=status, backend_type_id=backend_type_id, backend_id__isnull=backend_id__isnull, backend_id=backend_id, queued_at__isnull=queued_at__isnull, queued_at=queued_at, reserved_at__isnull=reserved_at__isnull, reserved_at=reserved_at, finished_at__isnull=finished_at__isnull, finished_at=finished_at, aggregated_algorithm_type=aggregated_algorithm_type, sort_by=sort_by, latest=latest, page=page, size=size)
        print("The response of BatchJobsApi->read_batch_jobs_batch_jobs_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BatchJobsApi->read_batch_jobs_batch_jobs_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | [optional] 
 **created_on** | **datetime**|  | [optional] 
 **status** | [**BatchJobStatus**](.md)|  | [optional] 
 **backend_type_id** | **int**|  | [optional] 
 **backend_id__isnull** | **bool**|  | [optional] 
 **backend_id** | **int**|  | [optional] 
 **queued_at__isnull** | **bool**|  | [optional] 
 **queued_at** | **datetime**|  | [optional] 
 **reserved_at__isnull** | **bool**|  | [optional] 
 **reserved_at** | **datetime**|  | [optional] 
 **finished_at__isnull** | **bool**|  | [optional] 
 **finished_at** | **datetime**|  | [optional] 
 **aggregated_algorithm_type** | [**AlgorithmType**](.md)|  | [optional] 
 **sort_by** | **str**| The field name to sort on. Prefix with &#39;-&#39; for descending order. E.g., &#39;-created_on&#39;. | [optional] 
 **latest** | **bool**| If True gets the most recently created object. | [optional] 
 **page** | **int**| Page number | [optional] [default to 1]
 **size** | **int**| Page size | [optional] [default to 50]

### Return type

[**PageBatchJob**](PageBatchJob.md)

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

# **unpop_batch_job_batch_jobs_id_unpop_patch**
> BatchJob unpop_batch_job_batch_jobs_id_unpop_patch(id)

Take batch job

Unclaim batch job.

### Example

* Api Key Authentication (backend):

```python
import compute_api_client
from compute_api_client.models.batch_job import BatchJob
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
    api_instance = compute_api_client.BatchJobsApi(api_client)
    id = 56 # int | 

    try:
        # Take batch job
        api_response = await api_instance.unpop_batch_job_batch_jobs_id_unpop_patch(id)
        print("The response of BatchJobsApi->unpop_batch_job_batch_jobs_id_unpop_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BatchJobsApi->unpop_batch_job_batch_jobs_id_unpop_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**BatchJob**](BatchJob.md)

### Authorization

[backend](../README.md#backend)

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

