# V1Dashboard


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] [readonly] 
**create_time** | **datetime** | Output only. Timestamp when the Dashboard was created. | [optional] [readonly] 
**creator** | **str** | Output only. Name of the user or service that requested creation of the Dashboard. | [optional] [readonly] 
**update_time** | **datetime** | Output only. Optional. Timestamp when the Dashboard was last updated. | [optional] [readonly] 
**updater** | **str** | Output only. Optional. Name of the user or service that requested update of the Dashboard. | [optional] [readonly] 
**delete_time** | **datetime** | Output only. Optional. Set when the Dashboard is deleted. When set Dashboard should be considered as deleted. | [optional] [readonly] 
**deleter** | **str** | Output only. Optional. Name of the user or service that requested deletion of the Dashboard. | [optional] [readonly] 
**display_name** | **str** | Human readable name of the Dashboard. | [optional] 
**description** | **str** | Optional. Arbitrary description of the Dashboard. | [optional] 
**status** | [**V1DashboardStatus**](V1DashboardStatus.md) |  | [optional] 
**leaderboards** | **List[str]** | Immutable. Resource names of the Leaderboards used in this Dashboard. | [optional] 
**create_operation** | **str** | Output only. Operation resource name that created this Dashboard. | [optional] [readonly] 
**demo** | **bool** | Output only. Whether the Dashboard is a demo resource or not. Demo resources are read only. | [optional] [readonly] 
**type** | [**V1DashboardType**](V1DashboardType.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_dashboard import V1Dashboard

# TODO update the JSON string below
json = "{}"
# create an instance of V1Dashboard from a JSON string
v1_dashboard_instance = V1Dashboard.from_json(json)
# print the JSON string representation of the object
print(V1Dashboard.to_json())

# convert the object into a dict
v1_dashboard_dict = v1_dashboard_instance.to_dict()
# create an instance of V1Dashboard from a dict
v1_dashboard_from_dict = V1Dashboard.from_dict(v1_dashboard_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


