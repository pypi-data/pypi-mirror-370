# V1LeaderboardReport

LeaderboardReport represents the leaderboard report which is formed by the results, models and evaluator.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**results** | [**List[V1LeaderboardReportResult]**](V1LeaderboardReportResult.md) | Output only. List of per test case results. | [optional] [readonly] 
**models** | [**List[V1LeaderboardReportModel]**](V1LeaderboardReportModel.md) | Output only. List of models which were used to create the results. | [optional] [readonly] 
**evaluator** | [**V1LeaderboardReportEvaluator**](V1LeaderboardReportEvaluator.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_leaderboard_report import V1LeaderboardReport

# TODO update the JSON string below
json = "{}"
# create an instance of V1LeaderboardReport from a JSON string
v1_leaderboard_report_instance = V1LeaderboardReport.from_json(json)
# print the JSON string representation of the object
print(V1LeaderboardReport.to_json())

# convert the object into a dict
v1_leaderboard_report_dict = v1_leaderboard_report_instance.to_dict()
# create an instance of V1LeaderboardReport from a dict
v1_leaderboard_report_from_dict = V1LeaderboardReport.from_dict(v1_leaderboard_report_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


