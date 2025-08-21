# WorkflowServiceCloneWorkflowRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**display_name_override** | **str** | Optional. The display name of the cloned Workflow. If not specified, the display name from the original Workflow is used with \&quot; Clone\&quot; suffix added. | [optional] 
**description_override** | **str** | Optional. The description of the cloned Workflow. If not specified, the description from the original Workflow is used. | [optional] 
**model_override** | **str** | Optional. The name of the model to use in the cloned Workflow. If not specified, the model from the original Workflow is used. | [optional] 
**llm_model_override** | **str** | Optional. The name of the base LLM model to use in the cloned workflow. If not specified, the base LLM model from the original Workflow is used. Required if model_override is set. | [optional] 
**model_parameters_override** | **str** | Optional. Model specific parameters in JSON format. If not specified, the parameters from the original Workflow are used. | [optional] 

## Example

```python
from eval_studio_client.api.models.workflow_service_clone_workflow_request import WorkflowServiceCloneWorkflowRequest

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowServiceCloneWorkflowRequest from a JSON string
workflow_service_clone_workflow_request_instance = WorkflowServiceCloneWorkflowRequest.from_json(json)
# print the JSON string representation of the object
print(WorkflowServiceCloneWorkflowRequest.to_json())

# convert the object into a dict
workflow_service_clone_workflow_request_dict = workflow_service_clone_workflow_request_instance.to_dict()
# create an instance of WorkflowServiceCloneWorkflowRequest from a dict
workflow_service_clone_workflow_request_from_dict = WorkflowServiceCloneWorkflowRequest.from_dict(workflow_service_clone_workflow_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


