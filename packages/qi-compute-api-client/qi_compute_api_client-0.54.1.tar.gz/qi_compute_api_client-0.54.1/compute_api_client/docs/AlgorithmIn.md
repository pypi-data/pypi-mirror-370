# AlgorithmIn


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**project_id** | **int** | ID of the project | 
**type** | [**AlgorithmType**](AlgorithmType.md) | The type of algorithm i.e. hybrid or quantum | 
**shared** | [**ShareType**](ShareType.md) | The sharing scope of the algorithm | 
**link** | **str** |  | [optional] 
**name** | **str** | The name of the algorithm | 

## Example

```python
from compute_api_client.models.algorithm_in import AlgorithmIn

# TODO update the JSON string below
json = "{}"
# create an instance of AlgorithmIn from a JSON string
algorithm_in_instance = AlgorithmIn.from_json(json)
# print the JSON string representation of the object
print(AlgorithmIn.to_json())

# convert the object into a dict
algorithm_in_dict = algorithm_in_instance.to_dict()
# create an instance of AlgorithmIn from a dict
algorithm_in_from_dict = AlgorithmIn.from_dict(algorithm_in_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


