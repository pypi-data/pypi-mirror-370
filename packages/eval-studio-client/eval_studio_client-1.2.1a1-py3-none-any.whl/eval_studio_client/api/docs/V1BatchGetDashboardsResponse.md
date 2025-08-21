# V1BatchGetDashboardsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dashboards** | [**List[V1Dashboard]**](V1Dashboard.md) | The requested Dashboards. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_batch_get_dashboards_response import V1BatchGetDashboardsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1BatchGetDashboardsResponse from a JSON string
v1_batch_get_dashboards_response_instance = V1BatchGetDashboardsResponse.from_json(json)
# print the JSON string representation of the object
print(V1BatchGetDashboardsResponse.to_json())

# convert the object into a dict
v1_batch_get_dashboards_response_dict = v1_batch_get_dashboards_response_instance.to_dict()
# create an instance of V1BatchGetDashboardsResponse from a dict
v1_batch_get_dashboards_response_from_dict = V1BatchGetDashboardsResponse.from_dict(v1_batch_get_dashboards_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


