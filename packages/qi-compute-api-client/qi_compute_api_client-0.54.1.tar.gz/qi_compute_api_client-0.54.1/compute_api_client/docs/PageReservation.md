# PageReservation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[Reservation]**](Reservation.md) |  | 
**total** | **int** |  | [optional] 
**page** | **int** |  | 
**size** | **int** |  | 
**pages** | **int** |  | [optional] 

## Example

```python
from compute_api_client.models.page_reservation import PageReservation

# TODO update the JSON string below
json = "{}"
# create an instance of PageReservation from a JSON string
page_reservation_instance = PageReservation.from_json(json)
# print the JSON string representation of the object
print(PageReservation.to_json())

# convert the object into a dict
page_reservation_dict = page_reservation_instance.to_dict()
# create an instance of PageReservation from a dict
page_reservation_from_dict = PageReservation.from_dict(page_reservation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


