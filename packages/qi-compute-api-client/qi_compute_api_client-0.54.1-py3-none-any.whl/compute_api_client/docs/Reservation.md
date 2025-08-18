# Reservation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | The id of the reservation | 
**member_id** | **int** | The id of the member who made the reservation | 
**start_time** | **datetime** | Starting time of lthe reservation | 
**end_time** | **datetime** | End time of the reservation | 
**backend_type_id** | **int** | The id of the backend_type | 
**backend_id** | **int** |  | 
**is_terminated** | **bool** | If the reservation has been terminated | 

## Example

```python
from compute_api_client.models.reservation import Reservation

# TODO update the JSON string below
json = "{}"
# create an instance of Reservation from a JSON string
reservation_instance = Reservation.from_json(json)
# print the JSON string representation of the object
print(Reservation.to_json())

# convert the object into a dict
reservation_dict = reservation_instance.to_dict()
# create an instance of Reservation from a dict
reservation_from_dict = Reservation.from_dict(reservation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


