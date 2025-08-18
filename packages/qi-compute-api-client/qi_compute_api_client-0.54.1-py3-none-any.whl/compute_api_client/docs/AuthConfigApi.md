# compute_api_client.AuthConfigApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**auth_config_auth_config_get**](AuthConfigApi.md#auth_config_auth_config_get) | **GET** /auth_config | Get suggested authentication configuration


# **auth_config_auth_config_get**
> AuthConfig auth_config_auth_config_get()

Get suggested authentication configuration

### Example


```python
import compute_api_client
from compute_api_client.models.auth_config import AuthConfig
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
    api_instance = compute_api_client.AuthConfigApi(api_client)

    try:
        # Get suggested authentication configuration
        api_response = await api_instance.auth_config_auth_config_get()
        print("The response of AuthConfigApi->auth_config_auth_config_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthConfigApi->auth_config_auth_config_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**AuthConfig**](AuthConfig.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

