# V1LeaderboardReportEvaluatorParameter

Evaluation parameter definition.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Output only. Evaluator parameter ID. | [optional] [readonly] 
**description** | **str** | Output only. Parameter description. | [optional] [readonly] 
**comment** | **str** | Optional. Parameter comment. | [optional] 
**type** | **str** | Output only. Parameter type like float or string. | [optional] [readonly] 
**predefined** | **List[object]** | Optional. Predefined parameter values - numeric or non-numeric enum. | [optional] 
**tags** | **List[str]** | Optional. Parameter tags. | [optional] 
**min** | **float** | Optional. Parameter value lower range. | [optional] 
**max** | **float** | Optional. Parameter value upper range. | [optional] 
**category** | **str** | Optional. Parameter category. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_leaderboard_report_evaluator_parameter import V1LeaderboardReportEvaluatorParameter

# TODO update the JSON string below
json = "{}"
# create an instance of V1LeaderboardReportEvaluatorParameter from a JSON string
v1_leaderboard_report_evaluator_parameter_instance = V1LeaderboardReportEvaluatorParameter.from_json(json)
# print the JSON string representation of the object
print(V1LeaderboardReportEvaluatorParameter.to_json())

# convert the object into a dict
v1_leaderboard_report_evaluator_parameter_dict = v1_leaderboard_report_evaluator_parameter_instance.to_dict()
# create an instance of V1LeaderboardReportEvaluatorParameter from a dict
v1_leaderboard_report_evaluator_parameter_from_dict = V1LeaderboardReportEvaluatorParameter.from_dict(v1_leaderboard_report_evaluator_parameter_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


