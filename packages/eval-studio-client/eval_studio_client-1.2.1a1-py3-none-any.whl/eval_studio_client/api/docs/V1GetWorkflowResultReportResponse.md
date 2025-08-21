# V1GetWorkflowResultReportResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**report_static** | **str** | Report without links. | [optional] 
**report_hypertext_diff** | **Dict[str, str]** | Diff (row number to row content) which can be used to generate report with links to the artifacts. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_get_workflow_result_report_response import V1GetWorkflowResultReportResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1GetWorkflowResultReportResponse from a JSON string
v1_get_workflow_result_report_response_instance = V1GetWorkflowResultReportResponse.from_json(json)
# print the JSON string representation of the object
print(V1GetWorkflowResultReportResponse.to_json())

# convert the object into a dict
v1_get_workflow_result_report_response_dict = v1_get_workflow_result_report_response_instance.to_dict()
# create an instance of V1GetWorkflowResultReportResponse from a dict
v1_get_workflow_result_report_response_from_dict = V1GetWorkflowResultReportResponse.from_dict(v1_get_workflow_result_report_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


