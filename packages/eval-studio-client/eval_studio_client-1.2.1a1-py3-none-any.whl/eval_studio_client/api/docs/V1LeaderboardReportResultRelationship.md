# V1LeaderboardReportResultRelationship

Relationship represents the relationship between result entries.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** | Output only. Type of the relationship. | [optional] [readonly] 
**target** | **str** | Output only. Source result of the relationship. | [optional] [readonly] 
**target_type** | **str** | Output only. Target type of the relationship like test_case. | [optional] [readonly] 

## Example

```python
from eval_studio_client.api.models.v1_leaderboard_report_result_relationship import V1LeaderboardReportResultRelationship

# TODO update the JSON string below
json = "{}"
# create an instance of V1LeaderboardReportResultRelationship from a JSON string
v1_leaderboard_report_result_relationship_instance = V1LeaderboardReportResultRelationship.from_json(json)
# print the JSON string representation of the object
print(V1LeaderboardReportResultRelationship.to_json())

# convert the object into a dict
v1_leaderboard_report_result_relationship_dict = v1_leaderboard_report_result_relationship_instance.to_dict()
# create an instance of V1LeaderboardReportResultRelationship from a dict
v1_leaderboard_report_result_relationship_from_dict = V1LeaderboardReportResultRelationship.from_dict(v1_leaderboard_report_result_relationship_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


