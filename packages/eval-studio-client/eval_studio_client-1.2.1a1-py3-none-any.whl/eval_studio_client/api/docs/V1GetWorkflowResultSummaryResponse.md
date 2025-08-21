# V1GetWorkflowResultSummaryResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**intro** | **str** | The 3x3x3 workflow summary: 3 summary sentences + 3 bullets with most serious highlights + 3 recommended actions sentences. | [optional] 
**bullets** | **List[str]** |  | [optional] 
**actions** | **str** |  | [optional] 
**artifact_types** | [**List[V1WorkflowResultArtifactType]**](V1WorkflowResultArtifactType.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_get_workflow_result_summary_response import V1GetWorkflowResultSummaryResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1GetWorkflowResultSummaryResponse from a JSON string
v1_get_workflow_result_summary_response_instance = V1GetWorkflowResultSummaryResponse.from_json(json)
# print the JSON string representation of the object
print(V1GetWorkflowResultSummaryResponse.to_json())

# convert the object into a dict
v1_get_workflow_result_summary_response_dict = v1_get_workflow_result_summary_response_instance.to_dict()
# create an instance of V1GetWorkflowResultSummaryResponse from a dict
v1_get_workflow_result_summary_response_from_dict = V1GetWorkflowResultSummaryResponse.from_dict(v1_get_workflow_result_summary_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


