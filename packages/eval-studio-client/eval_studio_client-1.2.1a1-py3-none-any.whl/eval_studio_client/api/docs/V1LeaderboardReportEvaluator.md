# V1LeaderboardReportEvaluator

Evaluator represents the evaluator which evaluated the model outputs to create the results.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Output only. Evaluator ID. | [optional] [readonly] 
**name** | **str** | Output only. Evaluator short name based on its class name. | [optional] [readonly] 
**display_name** | **str** | Output only. Evaluator display name. | [optional] [readonly] 
**tagline** | **str** | Optional. Evaluator one row description. | [optional] 
**description** | **str** | Output only. Evaluator description. | [optional] [readonly] 
**brief_description** | **str** | Optional. Brief description. | [optional] 
**model_types** | **List[str]** | Output only. List of model types like rag. | [optional] [readonly] 
**can_explain** | **List[str]** | Optional. List of experiment types the Explainer can explain like regression or multinomial. | [optional] 
**explanation_scopes** | **List[str]** | Output only. List of explanation scopes like global or local. | [optional] [readonly] 
**explanations** | [**List[V1LeaderboardReportExplanation]**](V1LeaderboardReportExplanation.md) | Output only. List of explanation types created by the Evaluator. | [optional] [readonly] 
**parameters** | [**List[V1LeaderboardReportEvaluatorParameter]**](V1LeaderboardReportEvaluatorParameter.md) | Output only. List of parameter type definitions. | [optional] [readonly] 
**keywords** | **List[str]** | Output only. List of keywords. | [optional] [readonly] 
**metrics_meta** | [**List[V1LeaderboardReportMetricsMetaEntry]**](V1LeaderboardReportMetricsMetaEntry.md) | Output only. List of metrics metadata for metrics created by the Evaluator. | [optional] [readonly] 

## Example

```python
from eval_studio_client.api.models.v1_leaderboard_report_evaluator import V1LeaderboardReportEvaluator

# TODO update the JSON string below
json = "{}"
# create an instance of V1LeaderboardReportEvaluator from a JSON string
v1_leaderboard_report_evaluator_instance = V1LeaderboardReportEvaluator.from_json(json)
# print the JSON string representation of the object
print(V1LeaderboardReportEvaluator.to_json())

# convert the object into a dict
v1_leaderboard_report_evaluator_dict = v1_leaderboard_report_evaluator_instance.to_dict()
# create an instance of V1LeaderboardReportEvaluator from a dict
v1_leaderboard_report_evaluator_from_dict = V1LeaderboardReportEvaluator.from_dict(v1_leaderboard_report_evaluator_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


