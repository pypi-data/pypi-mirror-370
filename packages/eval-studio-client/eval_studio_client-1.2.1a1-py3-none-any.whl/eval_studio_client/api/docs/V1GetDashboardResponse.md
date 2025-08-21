# V1GetDashboardResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dashboard** | [**V1Dashboard**](V1Dashboard.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_get_dashboard_response import V1GetDashboardResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1GetDashboardResponse from a JSON string
v1_get_dashboard_response_instance = V1GetDashboardResponse.from_json(json)
# print the JSON string representation of the object
print(V1GetDashboardResponse.to_json())

# convert the object into a dict
v1_get_dashboard_response_dict = v1_get_dashboard_response_instance.to_dict()
# create an instance of V1GetDashboardResponse from a dict
v1_get_dashboard_response_from_dict = V1GetDashboardResponse.from_dict(v1_get_dashboard_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


