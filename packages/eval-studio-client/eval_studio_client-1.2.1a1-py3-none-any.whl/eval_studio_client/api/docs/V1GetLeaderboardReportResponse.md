# V1GetLeaderboardReportResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**leaderboard_report** | [**V1LeaderboardReport**](V1LeaderboardReport.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_get_leaderboard_report_response import V1GetLeaderboardReportResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1GetLeaderboardReportResponse from a JSON string
v1_get_leaderboard_report_response_instance = V1GetLeaderboardReportResponse.from_json(json)
# print the JSON string representation of the object
print(V1GetLeaderboardReportResponse.to_json())

# convert the object into a dict
v1_get_leaderboard_report_response_dict = v1_get_leaderboard_report_response_instance.to_dict()
# create an instance of V1GetLeaderboardReportResponse from a dict
v1_get_leaderboard_report_response_from_dict = V1GetLeaderboardReportResponse.from_dict(v1_get_leaderboard_report_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


