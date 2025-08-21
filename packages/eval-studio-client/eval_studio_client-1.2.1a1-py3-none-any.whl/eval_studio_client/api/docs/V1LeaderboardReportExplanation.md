# V1LeaderboardReportExplanation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**explanation_type** | **str** | Output only. Explanation type ID. | [optional] [readonly] 
**name** | **str** | Output only. Explanation display name. | [optional] [readonly] 
**category** | **str** | Output only. Explanation display category. | [optional] [readonly] 
**scope** | **str** | Optional. Explanation scope like global or local. | [optional] 
**has_local** | **str** | Optional. Local explanation type id associated with (this) global explanation. | [optional] 
**formats** | **List[str]** | Optional. List of formats available for the explanation. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_leaderboard_report_explanation import V1LeaderboardReportExplanation

# TODO update the JSON string below
json = "{}"
# create an instance of V1LeaderboardReportExplanation from a JSON string
v1_leaderboard_report_explanation_instance = V1LeaderboardReportExplanation.from_json(json)
# print the JSON string representation of the object
print(V1LeaderboardReportExplanation.to_json())

# convert the object into a dict
v1_leaderboard_report_explanation_dict = v1_leaderboard_report_explanation_instance.to_dict()
# create an instance of V1LeaderboardReportExplanation from a dict
v1_leaderboard_report_explanation_from_dict = V1LeaderboardReportExplanation.from_dict(v1_leaderboard_report_explanation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


