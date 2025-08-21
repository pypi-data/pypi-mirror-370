# V1LeaderboardReportActualOutputData

ActualOutputData represents the actual output data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**text** | **str** | Output only. Text fragment. | [optional] [readonly] 
**metrics** | **object** | Output only. Metrics parsed as string to Value map. | [optional] [readonly] 

## Example

```python
from eval_studio_client.api.models.v1_leaderboard_report_actual_output_data import V1LeaderboardReportActualOutputData

# TODO update the JSON string below
json = "{}"
# create an instance of V1LeaderboardReportActualOutputData from a JSON string
v1_leaderboard_report_actual_output_data_instance = V1LeaderboardReportActualOutputData.from_json(json)
# print the JSON string representation of the object
print(V1LeaderboardReportActualOutputData.to_json())

# convert the object into a dict
v1_leaderboard_report_actual_output_data_dict = v1_leaderboard_report_actual_output_data_instance.to_dict()
# create an instance of V1LeaderboardReportActualOutputData from a dict
v1_leaderboard_report_actual_output_data_from_dict = V1LeaderboardReportActualOutputData.from_dict(v1_leaderboard_report_actual_output_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


