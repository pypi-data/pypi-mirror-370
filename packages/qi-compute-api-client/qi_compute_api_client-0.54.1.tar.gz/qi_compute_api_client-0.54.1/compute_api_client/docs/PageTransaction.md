# PageTransaction


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[Transaction]**](Transaction.md) |  | 
**total** | **int** |  | [optional] 
**page** | **int** |  | 
**size** | **int** |  | 
**pages** | **int** |  | [optional] 

## Example

```python
from compute_api_client.models.page_transaction import PageTransaction

# TODO update the JSON string below
json = "{}"
# create an instance of PageTransaction from a JSON string
page_transaction_instance = PageTransaction.from_json(json)
# print the JSON string representation of the object
print(PageTransaction.to_json())

# convert the object into a dict
page_transaction_dict = page_transaction_instance.to_dict()
# create an instance of PageTransaction from a dict
page_transaction_from_dict = PageTransaction.from_dict(page_transaction_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


