# V1LeaderboardReportMetricsMetaEntry

MetricsMetaEntry represents the metadata about the metric.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**key** | **str** | Output only. Metric key. | [optional] [readonly] 
**display_name** | **str** | Output only. Metric display name. | [optional] [readonly] 
**data_type** | **str** | Output only. Metric data type like float or string. | [optional] [readonly] 
**display_value** | **str** | Output only. Metric display value. | [optional] [readonly] 
**description** | **str** | Output only. Metric description. | [optional] [readonly] 
**value_range** | **List[float]** | Optional. Metric value range for numeric scores. | [optional] 
**value_enum** | **List[str]** | Optional. Metric value enum for non-numeric scores. | [optional] 
**higher_is_better** | **bool** | Output only. Metric higher is better. | [optional] [readonly] 
**threshold** | **float** | Output only. Metric threshold. | [optional] [readonly] 
**is_primary_metric** | **bool** | Output only. Metric is primary. | [optional] [readonly] 
**parent_metric** | **str** | Output only. This metric parent. | [optional] [readonly] 
**exclude** | **bool** | Output only. Whether to exclude the metric. | [optional] [readonly] 

## Example

```python
from eval_studio_client.api.models.v1_leaderboard_report_metrics_meta_entry import V1LeaderboardReportMetricsMetaEntry

# TODO update the JSON string below
json = "{}"
# create an instance of V1LeaderboardReportMetricsMetaEntry from a JSON string
v1_leaderboard_report_metrics_meta_entry_instance = V1LeaderboardReportMetricsMetaEntry.from_json(json)
# print the JSON string representation of the object
print(V1LeaderboardReportMetricsMetaEntry.to_json())

# convert the object into a dict
v1_leaderboard_report_metrics_meta_entry_dict = v1_leaderboard_report_metrics_meta_entry_instance.to_dict()
# create an instance of V1LeaderboardReportMetricsMetaEntry from a dict
v1_leaderboard_report_metrics_meta_entry_from_dict = V1LeaderboardReportMetricsMetaEntry.from_dict(v1_leaderboard_report_metrics_meta_entry_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


