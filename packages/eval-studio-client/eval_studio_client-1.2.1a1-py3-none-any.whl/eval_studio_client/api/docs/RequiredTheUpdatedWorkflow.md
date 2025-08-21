# RequiredTheUpdatedWorkflow


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**display_name** | **str** | Human-readable name of the Workflow. | [optional] 
**description** | **str** | Optional description of the Workflow. | [optional] 
**create_time** | **datetime** | Output only. Immutable. Creation time of the Workflow. | [optional] [readonly] 
**creator** | **str** | Output only. Immutable. Name of the user or service that requested creation of the Workflow. | [optional] [readonly] 
**update_time** | **datetime** | Output only. Optional. Last update time of the Workflow. | [optional] [readonly] 
**updater** | **str** | Output only. Name of the user or service that requested update of the Workflow. | [optional] [readonly] 
**delete_time** | **datetime** | Output only. Optional. Deletion time of the Workflow. | [optional] [readonly] 
**deleter** | **str** | Output only. Name of the user or service that requested deletion of the Workflow. | [optional] [readonly] 
**type** | [**V1WorkflowType**](V1WorkflowType.md) |  | [optional] 
**model** | **str** | Immutable. Resource name of the Model associated with this Workflow. | [optional] 
**nodes** | **List[str]** | Output only. List of the WorkflowNodes in the Workflow. | [optional] [readonly] 
**edges** | **List[str]** | Output only. List of the WorkflowEdges in the Workflow. | [optional] [readonly] 
**outputs** | **Dict[str, object]** | Output only. Optional. Computed outputs of all the WorkflowNodes in the Workflow. | [optional] [readonly] 
**output_artifacts** | [**Dict[str, V1WorkflowNodeArtifacts]**](V1WorkflowNodeArtifacts.md) | Output only. Optional. List of the WorkflowNodeArtifacts produces by all the WorkflowNodes in the Workflow. | [optional] [readonly] 
**llm_model** | **str** | Immutable. LLM Model to use. | [optional] 
**model_parameters** | **str** | Optional. Immutable. Model parameter overrides in JSON format. | [optional] 
**document** | **str** | The resource name of a Document. | [optional] 
**h2ogpte_collection** | **str** | Existing h2oGPTe collection. | [optional] 
**cloned_from_workflow** | **str** | Optional. Output only. The Workflow that this Workflow was cloned from. | [optional] [readonly] 

## Example

```python
from eval_studio_client.api.models.required_the_updated_workflow import RequiredTheUpdatedWorkflow

# TODO update the JSON string below
json = "{}"
# create an instance of RequiredTheUpdatedWorkflow from a JSON string
required_the_updated_workflow_instance = RequiredTheUpdatedWorkflow.from_json(json)
# print the JSON string representation of the object
print(RequiredTheUpdatedWorkflow.to_json())

# convert the object into a dict
required_the_updated_workflow_dict = required_the_updated_workflow_instance.to_dict()
# create an instance of RequiredTheUpdatedWorkflow from a dict
required_the_updated_workflow_from_dict = RequiredTheUpdatedWorkflow.from_dict(required_the_updated_workflow_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


