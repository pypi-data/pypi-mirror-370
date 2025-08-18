# HTTPNotFoundError


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**detail** | **str** |  | 

## Example

```python
from compute_api_client.models.http_not_found_error import HTTPNotFoundError

# TODO update the JSON string below
json = "{}"
# create an instance of HTTPNotFoundError from a JSON string
http_not_found_error_instance = HTTPNotFoundError.from_json(json)
# print the JSON string representation of the object
print(HTTPNotFoundError.to_json())

# convert the object into a dict
http_not_found_error_dict = http_not_found_error_instance.to_dict()
# create an instance of HTTPNotFoundError from a dict
http_not_found_error_from_dict = HTTPNotFoundError.from_dict(http_not_found_error_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


