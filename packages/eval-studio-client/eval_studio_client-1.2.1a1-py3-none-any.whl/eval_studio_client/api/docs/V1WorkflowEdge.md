# V1WorkflowEdge

WorkflowEdge represents an oriented edge between two WorkflowNodes in an Eval Studio Workflow.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Resource name of the Workflow in format of &#x60;workflow/{workflow_id}/edges/{edge_id}&#x60;. | [optional] 
**parent** | **str** | Output only. Immutable. Resource name of the parent Workflow in format of &#x60;workflow/{workflow_id}&#x60;. | [optional] [readonly] 
**create_time** | **datetime** | Output only. Immutable. Creation time of the WorkflowEdge. | [optional] [readonly] 
**creator** | **str** | Output only. Immutable. Name of the user or service that requested creation of the WorkflowEdge. | [optional] [readonly] 
**update_time** | **datetime** | Output only. Optional. Last update time of the WorkflowEdge. | [optional] [readonly] 
**updater** | **str** | Output only. Name of the user or service that requested update of the WorkflowEdge. | [optional] [readonly] 
**delete_time** | **datetime** | Output only. Optional. Deletion time of the WorkflowEdge. | [optional] [readonly] 
**deleter** | **str** | Output only. Name of the user or service that requested deletion of the WorkflowEdge. | [optional] [readonly] 
**type** | [**V1WorkflowEdgeType**](V1WorkflowEdgeType.md) |  | [optional] 
**var_from** | **str** | Resource name of the source WorkflowNode in format of &#x60;workflow/{workflow_id}/nodes/{node_id}&#x60;. | [optional] 
**to** | **str** | Resource name of the target WorkflowNode in format of &#x60;workflow/{workflow_id}/nodes/{node_id}&#x60;. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_workflow_edge import V1WorkflowEdge

# TODO update the JSON string below
json = "{}"
# create an instance of V1WorkflowEdge from a JSON string
v1_workflow_edge_instance = V1WorkflowEdge.from_json(json)
# print the JSON string representation of the object
print(V1WorkflowEdge.to_json())

# convert the object into a dict
v1_workflow_edge_dict = v1_workflow_edge_instance.to_dict()
# create an instance of V1WorkflowEdge from a dict
v1_workflow_edge_from_dict = V1WorkflowEdge.from_dict(v1_workflow_edge_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


