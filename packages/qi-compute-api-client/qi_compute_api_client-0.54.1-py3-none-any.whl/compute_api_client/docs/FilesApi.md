# compute_api_client.FilesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_file_files_post**](FilesApi.md#create_file_files_post) | **POST** /files | Create file
[**delete_file_files_id_delete**](FilesApi.md#delete_file_files_id_delete) | **DELETE** /files/{id} | Destroy file
[**read_file_files_id_get**](FilesApi.md#read_file_files_id_get) | **GET** /files/{id} | Retrieve file
[**read_files_files_get**](FilesApi.md#read_files_files_get) | **GET** /files | List files


# **create_file_files_post**
> File create_file_files_post(file_in)

Create file

Create new file.

### Example

* OAuth Authentication (user_bearer):

```python
import compute_api_client
from compute_api_client.models.file import File
from compute_api_client.models.file_in import FileIn
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
    api_instance = compute_api_client.FilesApi(api_client)
    file_in = compute_api_client.FileIn() # FileIn | 

    try:
        # Create file
        api_response = await api_instance.create_file_files_post(file_in)
        print("The response of FilesApi->create_file_files_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FilesApi->create_file_files_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_in** | [**FileIn**](FileIn.md)|  | 

### Return type

[**File**](File.md)

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

# **delete_file_files_id_delete**
> delete_file_files_id_delete(id)

Destroy file

Delete a file.

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
    api_instance = compute_api_client.FilesApi(api_client)
    id = 56 # int | 

    try:
        # Destroy file
        await api_instance.delete_file_files_id_delete(id)
    except Exception as e:
        print("Exception when calling FilesApi->delete_file_files_id_delete: %s\n" % e)
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

# **read_file_files_id_get**
> File read_file_files_id_get(id)

Retrieve file

Get file by ID.

### Example

* OAuth Authentication (user_bearer):
* Api Key Authentication (backend):

```python
import compute_api_client
from compute_api_client.models.file import File
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
    api_instance = compute_api_client.FilesApi(api_client)
    id = 56 # int | 

    try:
        # Retrieve file
        api_response = await api_instance.read_file_files_id_get(id)
        print("The response of FilesApi->read_file_files_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FilesApi->read_file_files_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**File**](File.md)

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

# **read_files_files_get**
> PageFile read_files_files_get(id=id, commit_id=commit_id, content=content, language_id=language_id, compile_stage=compile_stage, generated=generated, name__isnull=name__isnull, name=name, sort_by=sort_by, latest=latest, page=page, size=size)

List files

List files.

### Example

* OAuth Authentication (user_bearer):

```python
import compute_api_client
from compute_api_client.models.compile_stage import CompileStage
from compute_api_client.models.page_file import PageFile
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
    api_instance = compute_api_client.FilesApi(api_client)
    id = 56 # int |  (optional)
    commit_id = 56 # int |  (optional)
    content = 'content_example' # str |  (optional)
    language_id = 56 # int |  (optional)
    compile_stage = compute_api_client.CompileStage() # CompileStage |  (optional)
    generated = True # bool |  (optional)
    name__isnull = True # bool |  (optional)
    name = 'name_example' # str |  (optional)
    sort_by = 'sort_by_example' # str | The field name to sort on. Prefix with '-' for descending order. E.g., '-created_on'. (optional)
    latest = True # bool | If True gets the most recently created object. (optional)
    page = 1 # int | Page number (optional) (default to 1)
    size = 50 # int | Page size (optional) (default to 50)

    try:
        # List files
        api_response = await api_instance.read_files_files_get(id=id, commit_id=commit_id, content=content, language_id=language_id, compile_stage=compile_stage, generated=generated, name__isnull=name__isnull, name=name, sort_by=sort_by, latest=latest, page=page, size=size)
        print("The response of FilesApi->read_files_files_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FilesApi->read_files_files_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | [optional] 
 **commit_id** | **int**|  | [optional] 
 **content** | **str**|  | [optional] 
 **language_id** | **int**|  | [optional] 
 **compile_stage** | [**CompileStage**](.md)|  | [optional] 
 **generated** | **bool**|  | [optional] 
 **name__isnull** | **bool**|  | [optional] 
 **name** | **str**|  | [optional] 
 **sort_by** | **str**| The field name to sort on. Prefix with &#39;-&#39; for descending order. E.g., &#39;-created_on&#39;. | [optional] 
 **latest** | **bool**| If True gets the most recently created object. | [optional] 
 **page** | **int**| Page number | [optional] [default to 1]
 **size** | **int**| Page size | [optional] [default to 50]

### Return type

[**PageFile**](PageFile.md)

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

