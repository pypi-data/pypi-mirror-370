# V1CreateWorkflowEdgeResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**edge** | [**V1WorkflowEdge**](V1WorkflowEdge.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_create_workflow_edge_response import V1CreateWorkflowEdgeResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1CreateWorkflowEdgeResponse from a JSON string
v1_create_workflow_edge_response_instance = V1CreateWorkflowEdgeResponse.from_json(json)
# print the JSON string representation of the object
print(V1CreateWorkflowEdgeResponse.to_json())

# convert the object into a dict
v1_create_workflow_edge_response_dict = v1_create_workflow_edge_response_instance.to_dict()
# create an instance of V1CreateWorkflowEdgeResponse from a dict
v1_create_workflow_edge_response_from_dict = V1CreateWorkflowEdgeResponse.from_dict(v1_create_workflow_edge_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


