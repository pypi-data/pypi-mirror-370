# compute_api_client.ProjectsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_project_projects_post**](ProjectsApi.md#create_project_projects_post) | **POST** /projects | Create project
[**delete_project_projects_id_delete**](ProjectsApi.md#delete_project_projects_id_delete) | **DELETE** /projects/{id} | Destroy project
[**partial_update_project_projects_id_patch**](ProjectsApi.md#partial_update_project_projects_id_patch) | **PATCH** /projects/{id} | Partially update project
[**read_project_projects_id_get**](ProjectsApi.md#read_project_projects_id_get) | **GET** /projects/{id} | Retrieve project
[**read_projects_projects_get**](ProjectsApi.md#read_projects_projects_get) | **GET** /projects | List projects
[**update_project_projects_id_put**](ProjectsApi.md#update_project_projects_id_put) | **PUT** /projects/{id} | Update project


# **create_project_projects_post**
> Project create_project_projects_post(project_in)

Create project

Create new project.

### Example

* OAuth Authentication (user_bearer):

```python
import compute_api_client
from compute_api_client.models.project import Project
from compute_api_client.models.project_in import ProjectIn
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
    api_instance = compute_api_client.ProjectsApi(api_client)
    project_in = compute_api_client.ProjectIn() # ProjectIn | 

    try:
        # Create project
        api_response = await api_instance.create_project_projects_post(project_in)
        print("The response of ProjectsApi->create_project_projects_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectsApi->create_project_projects_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_in** | [**ProjectIn**](ProjectIn.md)|  | 

### Return type

[**Project**](Project.md)

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

# **delete_project_projects_id_delete**
> delete_project_projects_id_delete(id)

Destroy project

Delete a project.

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
    api_instance = compute_api_client.ProjectsApi(api_client)
    id = 56 # int | 

    try:
        # Destroy project
        await api_instance.delete_project_projects_id_delete(id)
    except Exception as e:
        print("Exception when calling ProjectsApi->delete_project_projects_id_delete: %s\n" % e)
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

# **partial_update_project_projects_id_patch**
> Project partial_update_project_projects_id_patch(id, project_patch)

Partially update project

Partially update a project.

### Example

* OAuth Authentication (user_bearer):

```python
import compute_api_client
from compute_api_client.models.project import Project
from compute_api_client.models.project_patch import ProjectPatch
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
    api_instance = compute_api_client.ProjectsApi(api_client)
    id = 56 # int | 
    project_patch = compute_api_client.ProjectPatch() # ProjectPatch | 

    try:
        # Partially update project
        api_response = await api_instance.partial_update_project_projects_id_patch(id, project_patch)
        print("The response of ProjectsApi->partial_update_project_projects_id_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectsApi->partial_update_project_projects_id_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **project_patch** | [**ProjectPatch**](ProjectPatch.md)|  | 

### Return type

[**Project**](Project.md)

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

# **read_project_projects_id_get**
> Project read_project_projects_id_get(id)

Retrieve project

Get project by ID.

### Example

* OAuth Authentication (user_bearer):

```python
import compute_api_client
from compute_api_client.models.project import Project
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
    api_instance = compute_api_client.ProjectsApi(api_client)
    id = 56 # int | 

    try:
        # Retrieve project
        api_response = await api_instance.read_project_projects_id_get(id)
        print("The response of ProjectsApi->read_project_projects_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectsApi->read_project_projects_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 

### Return type

[**Project**](Project.md)

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

# **read_projects_projects_get**
> PageProject read_projects_projects_get(search=search, id=id, created_on=created_on, owner_id=owner_id, name=name, description=description, starred=starred, sort_by=sort_by, latest=latest, page=page, size=size)

List projects

List projects.

If the search parameter is provided, the list is filtered based on the condition that either the project name OR
description contains the specified substring. The filter considers exact matches for other parameters provided. The
final result is the logical AND of the substring match condition and any other provided exact match conditions.

### Example

* OAuth Authentication (user_bearer):

```python
import compute_api_client
from compute_api_client.models.page_project import PageProject
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
    api_instance = compute_api_client.ProjectsApi(api_client)
    search = 'search_example' # str | Substring search for project names or description (optional)
    id = 56 # int |  (optional)
    created_on = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    owner_id = 56 # int |  (optional)
    name = 'name_example' # str |  (optional)
    description = 'description_example' # str |  (optional)
    starred = True # bool |  (optional)
    sort_by = 'sort_by_example' # str | The field name to sort on. Prefix with '-' for descending order. E.g., '-created_on'. (optional)
    latest = True # bool | If True gets the most recently created object. (optional)
    page = 1 # int | Page number (optional) (default to 1)
    size = 50 # int | Page size (optional) (default to 50)

    try:
        # List projects
        api_response = await api_instance.read_projects_projects_get(search=search, id=id, created_on=created_on, owner_id=owner_id, name=name, description=description, starred=starred, sort_by=sort_by, latest=latest, page=page, size=size)
        print("The response of ProjectsApi->read_projects_projects_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectsApi->read_projects_projects_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **search** | **str**| Substring search for project names or description | [optional] 
 **id** | **int**|  | [optional] 
 **created_on** | **datetime**|  | [optional] 
 **owner_id** | **int**|  | [optional] 
 **name** | **str**|  | [optional] 
 **description** | **str**|  | [optional] 
 **starred** | **bool**|  | [optional] 
 **sort_by** | **str**| The field name to sort on. Prefix with &#39;-&#39; for descending order. E.g., &#39;-created_on&#39;. | [optional] 
 **latest** | **bool**| If True gets the most recently created object. | [optional] 
 **page** | **int**| Page number | [optional] [default to 1]
 **size** | **int**| Page size | [optional] [default to 50]

### Return type

[**PageProject**](PageProject.md)

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

# **update_project_projects_id_put**
> Project update_project_projects_id_put(id, project_in)

Update project

Update a project.

### Example

* OAuth Authentication (user_bearer):

```python
import compute_api_client
from compute_api_client.models.project import Project
from compute_api_client.models.project_in import ProjectIn
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
    api_instance = compute_api_client.ProjectsApi(api_client)
    id = 56 # int | 
    project_in = compute_api_client.ProjectIn() # ProjectIn | 

    try:
        # Update project
        api_response = await api_instance.update_project_projects_id_put(id, project_in)
        print("The response of ProjectsApi->update_project_projects_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProjectsApi->update_project_projects_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **int**|  | 
 **project_in** | [**ProjectIn**](ProjectIn.md)|  | 

### Return type

[**Project**](Project.md)

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

