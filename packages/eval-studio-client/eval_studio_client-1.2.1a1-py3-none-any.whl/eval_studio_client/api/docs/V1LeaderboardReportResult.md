# V1LeaderboardReportResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**key** | **str** | Output only. Composite unique key of the result formed by the model key and test case key. | [optional] [readonly] 
**input** | **str** | Output only. Input prompt or text to be processed. | [optional] [readonly] 
**corpus** | **List[str]** | Output only. Collection of corpus documents to be used during evaluation. | [optional] [readonly] 
**context** | **List[str]** | Output only. List of contextual information or references. | [optional] [readonly] 
**categories** | **List[str]** | Output only. List of categories or labels for classification. | [optional] [readonly] 
**relationships** | [**List[V1LeaderboardReportResultRelationship]**](V1LeaderboardReportResultRelationship.md) | Output only. List of relationships or associations between entities. | [optional] [readonly] 
**expected_output** | **str** | Output only. Expected output or target result. | [optional] [readonly] 
**output_constraints** | **List[str]** | Output only. List of constraints that should be applied to the output. | [optional] [readonly] 
**output_condition** | **str** | Output only. Condition that output should satisfy. | [optional] [readonly] 
**actual_output** | **str** | Output only. Actual output produced by the model. | [optional] [readonly] 
**actual_duration** | **float** | Output only. Duration of processing in seconds. | [optional] [readonly] 
**cost** | **float** | Output only. Cost of processing in currency units. | [optional] [readonly] 
**model_key** | **str** | Output only. Unique identifier for the model used. | [optional] [readonly] 
**test_case_key** | **str** | Output only. Unique identifier for the test case. | [optional] [readonly] 
**metrics** | [**List[V1MetricScore]**](V1MetricScore.md) | Optional. All metrics values for the result. | [optional] 
**result_error_message** | **str** | Output only. Error message if processing resulted in failure. | [optional] [readonly] 
**actual_output_meta** | [**List[V1LeaderboardReportActualOutputMeta]**](V1LeaderboardReportActualOutputMeta.md) | Output only. Additional metadata about the actual output. | [optional] [readonly] 

## Example

```python
from eval_studio_client.api.models.v1_leaderboard_report_result import V1LeaderboardReportResult

# TODO update the JSON string below
json = "{}"
# create an instance of V1LeaderboardReportResult from a JSON string
v1_leaderboard_report_result_instance = V1LeaderboardReportResult.from_json(json)
# print the JSON string representation of the object
print(V1LeaderboardReportResult.to_json())

# convert the object into a dict
v1_leaderboard_report_result_dict = v1_leaderboard_report_result_instance.to_dict()
# create an instance of V1LeaderboardReportResult from a dict
v1_leaderboard_report_result_from_dict = V1LeaderboardReportResult.from_dict(v1_leaderboard_report_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


