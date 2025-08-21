# RequiredTheUpdatedWorkflowNode


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**parent** | **str** | Output only. Immutable. Resource name of the parent Workflow in format of &#x60;workflows/{workflow_id}/&#x60;. | [optional] [readonly] 
**display_name** | **str** | Human-readable name of the WorkflowNode. | [optional] 
**description** | **str** | Optional description of the WorkflowNode. | [optional] 
**create_time** | **datetime** | Output only. Immutable. Creation time of the WorkflowNode. | [optional] [readonly] 
**creator** | **str** | Output only. Immutable. Name of the user or service that requested creation of the WorkflowNode. | [optional] [readonly] 
**update_time** | **datetime** | Output only. Optional. Last update time of the WorkflowNode. | [optional] [readonly] 
**updater** | **str** | Output only. Name of the user or service that requested update of the WorkflowNode. | [optional] [readonly] 
**delete_time** | **datetime** | Output only. Optional. Deletion time of the WorkflowNode. | [optional] [readonly] 
**deleter** | **str** | Output only. Name of the user or service that requested deletion of the WorkflowNode. | [optional] [readonly] 
**type** | [**V1WorkflowNodeType**](V1WorkflowNodeType.md) |  | [optional] 
**parameters** | **object** | User-given parameters for the WorkflowNode. | [optional] 
**outputs** | **object** | Output only. Computed outputs of the WorkflowNode. | [optional] [readonly] 
**output_artifacts** | [**List[V1WorkflowNodeArtifact]**](V1WorkflowNodeArtifact.md) | Output only. Optional. List of the WorkflowNodeArtifacts produces by the WorkflowNode. | [optional] [readonly] 
**status** | [**V1WorkflowNodeStatus**](V1WorkflowNodeStatus.md) |  | [optional] 
**attributes** | [**V1WorkflowNodeAttributes**](V1WorkflowNodeAttributes.md) |  | [optional] 
**processed_by_operation** | **str** | Output only. Optional. Resource name of the latest Operation that has processed or is currently processing this WorkflowNode. | [optional] [readonly] 
**result_status** | [**V1WorkflowNodeResultStatus**](V1WorkflowNodeResultStatus.md) |  | [optional] 
**stale** | **bool** | Output only. The stale field marks whether the internal result is outdated and need to be checked for validity. | [optional] [readonly] 

## Example

```python
from eval_studio_client.api.models.required_the_updated_workflow_node import RequiredTheUpdatedWorkflowNode

# TODO update the JSON string below
json = "{}"
# create an instance of RequiredTheUpdatedWorkflowNode from a JSON string
required_the_updated_workflow_node_instance = RequiredTheUpdatedWorkflowNode.from_json(json)
# print the JSON string representation of the object
print(RequiredTheUpdatedWorkflowNode.to_json())

# convert the object into a dict
required_the_updated_workflow_node_dict = required_the_updated_workflow_node_instance.to_dict()
# create an instance of RequiredTheUpdatedWorkflowNode from a dict
required_the_updated_workflow_node_from_dict = RequiredTheUpdatedWorkflowNode.from_dict(required_the_updated_workflow_node_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


