# V1LeaderboardReportModel

Model represents the evaluated model whose outputs were evaluated to create the results.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**connection** | **str** | Output only. Connection key. | [optional] [readonly] 
**model_type** | **str** | Output only. Model type. | [optional] [readonly] 
**name** | **str** | Output only. Model display name. | [optional] [readonly] 
**collection_id** | **str** | Optional. Collection ID. | [optional] 
**collection_name** | **str** | Optional. Collection name. | [optional] 
**llm_model_name** | **str** | Output only. LLM model name. | [optional] [readonly] 
**documents** | **List[str]** | Output only. List of documents. | [optional] [readonly] 
**key** | **str** | Output only. Model key. | [optional] [readonly] 

## Example

```python
from eval_studio_client.api.models.v1_leaderboard_report_model import V1LeaderboardReportModel

# TODO update the JSON string below
json = "{}"
# create an instance of V1LeaderboardReportModel from a JSON string
v1_leaderboard_report_model_instance = V1LeaderboardReportModel.from_json(json)
# print the JSON string representation of the object
print(V1LeaderboardReportModel.to_json())

# convert the object into a dict
v1_leaderboard_report_model_dict = v1_leaderboard_report_model_instance.to_dict()
# create an instance of V1LeaderboardReportModel from a dict
v1_leaderboard_report_model_from_dict = V1LeaderboardReportModel.from_dict(v1_leaderboard_report_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


