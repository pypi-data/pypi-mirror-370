# V1WorkflowNodeArtifact

WorkflowNodeArtifact represents an artifact produced/consumed by a WorkflowNode.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Resource name of the Workflow in format of &#x60;workflows/{workflow_id}/nodes/{node_id}/artifacts/{artifact_id}&#x60;. | [optional] 
**parent** | **str** | Output only. Immutable. Resource name of the parent WorkflowNode in format of &#x60;workflows/{workflow_id}/nodes/{node_id}&#x60;. | [optional] [readonly] 
**display_name** | **str** | Human-readable name of the WorkflowNodeArtifact. | [optional] 
**description** | **str** | Optional description of the WorkflowNodeArtifact. | [optional] 
**create_time** | **datetime** | Output only. Immutable. Creation time of the WorkflowNodeArtifact. | [optional] [readonly] 
**creator** | **str** | Output only. Immutable. Name of the user or service that requested creation of the WorkflowNodeArtifact. | [optional] [readonly] 
**update_time** | **datetime** | Output only. Optional. Last update time of the WorkflowNodeArtifact. | [optional] [readonly] 
**updater** | **str** | Output only. Name of the user or service that requested update of the WorkflowNodeArtifact. | [optional] [readonly] 
**delete_time** | **datetime** | Output only. Optional. Deletion time of the WorkflowNodeArtifact. | [optional] [readonly] 
**deleter** | **str** | Output only. Name of the user or service that requested deletion of the WorkflowNodeArtifact. | [optional] [readonly] 
**mime_type** | **str** | Optional MIME type of the WorkflowNodeArtifact. | [optional] 
**type** | **str** | Output only. Immutable. Type of the WorkflowNodeArtifact. | [optional] [readonly] 

## Example

```python
from eval_studio_client.api.models.v1_workflow_node_artifact import V1WorkflowNodeArtifact

# TODO update the JSON string below
json = "{}"
# create an instance of V1WorkflowNodeArtifact from a JSON string
v1_workflow_node_artifact_instance = V1WorkflowNodeArtifact.from_json(json)
# print the JSON string representation of the object
print(V1WorkflowNodeArtifact.to_json())

# convert the object into a dict
v1_workflow_node_artifact_dict = v1_workflow_node_artifact_instance.to_dict()
# create an instance of V1WorkflowNodeArtifact from a dict
v1_workflow_node_artifact_from_dict = V1WorkflowNodeArtifact.from_dict(v1_workflow_node_artifact_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


