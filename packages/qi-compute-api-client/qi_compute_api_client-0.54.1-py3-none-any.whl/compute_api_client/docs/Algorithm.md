# Algorithm


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | ID of the algorithm | 
**project_id** | **int** | ID of the project | 
**type** | [**AlgorithmType**](AlgorithmType.md) | The type of algorithm i.e. hybrid or quantum | 
**shared** | [**ShareType**](ShareType.md) | The sharing scope of the algorithm | 
**link** | **str** |  | 
**name** | **str** | Name of the algorithm | 

## Example

```python
from compute_api_client.models.algorithm import Algorithm

# TODO update the JSON string below
json = "{}"
# create an instance of Algorithm from a JSON string
algorithm_instance = Algorithm.from_json(json)
# print the JSON string representation of the object
print(Algorithm.to_json())

# convert the object into a dict
algorithm_dict = algorithm_instance.to_dict()
# create an instance of Algorithm from a dict
algorithm_from_dict = Algorithm.from_dict(algorithm_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


