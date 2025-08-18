# ReservationIn


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**member_id** | **int** | The id of the member who made the reservation | 
**start_time** | **datetime** | Starting time of lthe reservation | 
**end_time** | **datetime** | End time of the reservation | 
**backend_type_id** | **int** | The id of the backend_type | 

## Example

```python
from compute_api_client.models.reservation_in import ReservationIn

# TODO update the JSON string below
json = "{}"
# create an instance of ReservationIn from a JSON string
reservation_in_instance = ReservationIn.from_json(json)
# print the JSON string representation of the object
print(ReservationIn.to_json())

# convert the object into a dict
reservation_in_dict = reservation_in_instance.to_dict()
# create an instance of ReservationIn from a dict
reservation_in_from_dict = ReservationIn.from_dict(reservation_in_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


