# compute_api_client.HealthApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**healthz_healthz_get**](HealthApi.md#healthz_healthz_get) | **GET** /healthz | Report health


# **healthz_healthz_get**
> object healthz_healthz_get()

Report health

Health endpoint.

### Example


```python
import compute_api_client
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
    api_instance = compute_api_client.HealthApi(api_client)

    try:
        # Report health
        api_response = await api_instance.healthz_healthz_get()
        print("The response of HealthApi->healthz_healthz_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling HealthApi->healthz_healthz_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**object**

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

