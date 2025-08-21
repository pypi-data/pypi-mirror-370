# V1BatchGetWorkflowNodesResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**nodes** | [**List[V1WorkflowNode]**](V1WorkflowNode.md) | The WorkflowNodes requested. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_batch_get_workflow_nodes_response import V1BatchGetWorkflowNodesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1BatchGetWorkflowNodesResponse from a JSON string
v1_batch_get_workflow_nodes_response_instance = V1BatchGetWorkflowNodesResponse.from_json(json)
# print the JSON string representation of the object
print(V1BatchGetWorkflowNodesResponse.to_json())

# convert the object into a dict
v1_batch_get_workflow_nodes_response_dict = v1_batch_get_workflow_nodes_response_instance.to_dict()
# create an instance of V1BatchGetWorkflowNodesResponse from a dict
v1_batch_get_workflow_nodes_response_from_dict = V1BatchGetWorkflowNodesResponse.from_dict(v1_batch_get_workflow_nodes_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


