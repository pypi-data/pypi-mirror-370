# RequiredTheLeaderboardToUpdate

The Leaderboard's `name` field is used to identify the Leaderboard to update. Format: leaderboards/{leaderboard}

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**create_time** | **datetime** | Output only. Timestamp when the Leaderboard was created. | [optional] [readonly] 
**creator** | **str** | Output only. Name of the user or service that requested creation of the Leaderboard. | [optional] [readonly] 
**update_time** | **datetime** | Output only. Optional. Timestamp when the Leaderboard was last updated. | [optional] [readonly] 
**updater** | **str** | Output only. Optional. Name of the user or service that requested update of the Leaderboard. | [optional] [readonly] 
**delete_time** | **datetime** | Output only. Optional. Set when the Leaderboard is deleted. When set Leaderboard should be considered as deleted. | [optional] [readonly] 
**deleter** | **str** | Output only. Optional. Name of the user or service that requested deletion of the Leaderboard. | [optional] [readonly] 
**display_name** | **str** | Human readable name of the Leaderboard. | [optional] 
**description** | **str** | Optional. Arbitrary description of the Leaderboard. | [optional] 
**status** | [**V1LeaderboardStatus**](V1LeaderboardStatus.md) |  | [optional] 
**evaluator** | **str** | Immutable. Resource name of the Evaluator used in this Leaderboard. | [optional] 
**tests** | **List[str]** | Immutable. Resource names of the Tests used in this Leaderboard. | [optional] 
**model** | **str** | Immutable. Resource name of the Model used in this Leaderboard. | [optional] 
**create_operation** | **str** | Output only. Operation resource name that created this Leaderboard. | [optional] [readonly] 
**leaderboard_report** | **str** |  | [optional] 
**leaderboard_table** | **str** | Output only. Leaderboard table in JSON format. | [optional] [readonly] 
**leaderboard_summary** | **str** | Output only. Leaderboard summary in Markdown format. | [optional] [readonly] 
**llm_models** | **List[str]** | Immutable. System names of the LLM models used in this Leaderboard. | [optional] 
**leaderboard_problems** | [**List[V1ProblemAndAction]**](V1ProblemAndAction.md) | Output only. Leaderboard problems and actions. | [optional] [readonly] 
**evaluator_parameters** | **str** | Optional. Evaluator parameters setup. | [optional] 
**insights** | [**List[V1Insight]**](V1Insight.md) | Output only. Insights from the Leaderboard. | [optional] [readonly] 
**model_parameters** | **str** | Optional. Prameters overrides in JSON format. | [optional] 
**h2ogpte_collection** | **str** | The existing collection name in H2OGPTe. | [optional] 
**type** | [**V1LeaderboardType**](V1LeaderboardType.md) |  | [optional] 
**demo** | **bool** | Output only. Whether the Leaderboard is a demo resource or not. Demo resources are read only. | [optional] [readonly] 
**test_lab** | **str** | Optional. Resource name of the TestLab if Leaderboard was created from a imported TestLab. | [optional] 

## Example

```python
from eval_studio_client.api.models.required_the_leaderboard_to_update import RequiredTheLeaderboardToUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of RequiredTheLeaderboardToUpdate from a JSON string
required_the_leaderboard_to_update_instance = RequiredTheLeaderboardToUpdate.from_json(json)
# print the JSON string representation of the object
print(RequiredTheLeaderboardToUpdate.to_json())

# convert the object into a dict
required_the_leaderboard_to_update_dict = required_the_leaderboard_to_update_instance.to_dict()
# create an instance of RequiredTheLeaderboardToUpdate from a dict
required_the_leaderboard_to_update_from_dict = RequiredTheLeaderboardToUpdate.from_dict(required_the_leaderboard_to_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


