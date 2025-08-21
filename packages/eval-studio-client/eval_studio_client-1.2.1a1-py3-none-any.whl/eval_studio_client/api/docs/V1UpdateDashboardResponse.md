# V1UpdateDashboardResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dashboard** | [**V1Dashboard**](V1Dashboard.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_update_dashboard_response import V1UpdateDashboardResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1UpdateDashboardResponse from a JSON string
v1_update_dashboard_response_instance = V1UpdateDashboardResponse.from_json(json)
# print the JSON string representation of the object
print(V1UpdateDashboardResponse.to_json())

# convert the object into a dict
v1_update_dashboard_response_dict = v1_update_dashboard_response_instance.to_dict()
# create an instance of V1UpdateDashboardResponse from a dict
v1_update_dashboard_response_from_dict = V1UpdateDashboardResponse.from_dict(v1_update_dashboard_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


