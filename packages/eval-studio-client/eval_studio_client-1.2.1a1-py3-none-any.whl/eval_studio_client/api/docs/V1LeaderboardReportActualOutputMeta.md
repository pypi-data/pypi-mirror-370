# V1LeaderboardReportActualOutputMeta

ActualOutputMeta represents the metadata about the actual output.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tokenization** | **str** | Output only. Actual output data tokenization like sentence_level_punkt. | [optional] [readonly] 
**data** | [**List[V1LeaderboardReportActualOutputData]**](V1LeaderboardReportActualOutputData.md) | Output only. Actual output data - list of text fragments coupled with the metric values. | [optional] [readonly] 

## Example

```python
from eval_studio_client.api.models.v1_leaderboard_report_actual_output_meta import V1LeaderboardReportActualOutputMeta

# TODO update the JSON string below
json = "{}"
# create an instance of V1LeaderboardReportActualOutputMeta from a JSON string
v1_leaderboard_report_actual_output_meta_instance = V1LeaderboardReportActualOutputMeta.from_json(json)
# print the JSON string representation of the object
print(V1LeaderboardReportActualOutputMeta.to_json())

# convert the object into a dict
v1_leaderboard_report_actual_output_meta_dict = v1_leaderboard_report_actual_output_meta_instance.to_dict()
# create an instance of V1LeaderboardReportActualOutputMeta from a dict
v1_leaderboard_report_actual_output_meta_from_dict = V1LeaderboardReportActualOutputMeta.from_dict(v1_leaderboard_report_actual_output_meta_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


