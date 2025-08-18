# HTTPBadRequestError


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**detail** | **str** |  | 

## Example

```python
from compute_api_client.models.http_bad_request_error import HTTPBadRequestError

# TODO update the JSON string below
json = "{}"
# create an instance of HTTPBadRequestError from a JSON string
http_bad_request_error_instance = HTTPBadRequestError.from_json(json)
# print the JSON string representation of the object
print(HTTPBadRequestError.to_json())

# convert the object into a dict
http_bad_request_error_dict = http_bad_request_error_instance.to_dict()
# create an instance of HTTPBadRequestError from a dict
http_bad_request_error_from_dict = HTTPBadRequestError.from_dict(http_bad_request_error_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


