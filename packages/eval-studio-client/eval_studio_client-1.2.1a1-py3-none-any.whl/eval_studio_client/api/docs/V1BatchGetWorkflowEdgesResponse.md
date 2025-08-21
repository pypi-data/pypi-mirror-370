# V1BatchGetWorkflowEdgesResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**edges** | [**List[V1WorkflowEdge]**](V1WorkflowEdge.md) | The WorkflowEdges requested. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_batch_get_workflow_edges_response import V1BatchGetWorkflowEdgesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1BatchGetWorkflowEdgesResponse from a JSON string
v1_batch_get_workflow_edges_response_instance = V1BatchGetWorkflowEdgesResponse.from_json(json)
# print the JSON string representation of the object
print(V1BatchGetWorkflowEdgesResponse.to_json())

# convert the object into a dict
v1_batch_get_workflow_edges_response_dict = v1_batch_get_workflow_edges_response_instance.to_dict()
# create an instance of V1BatchGetWorkflowEdgesResponse from a dict
v1_batch_get_workflow_edges_response_from_dict = V1BatchGetWorkflowEdgesResponse.from_dict(v1_batch_get_workflow_edges_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


