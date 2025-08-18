# Transaction


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | The id of the transaction | 
**domain** | [**Domain**](Domain.md) |  | 
**job** | **int** |  | 
**team_id** | **int** | The id of the team who initiated the transaction | 
**member_id** | **int** |  | 
**change** | **int** |  | 
**timestamp** | **datetime** | Time when the transaction was started | 

## Example

```python
from compute_api_client.models.transaction import Transaction

# TODO update the JSON string below
json = "{}"
# create an instance of Transaction from a JSON string
transaction_instance = Transaction.from_json(json)
# print the JSON string representation of the object
print(Transaction.to_json())

# convert the object into a dict
transaction_dict = transaction_instance.to_dict()
# create an instance of Transaction from a dict
transaction_from_dict = Transaction.from_dict(transaction_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


