# V1InitWorkflowNodeResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**node** | [**V1WorkflowNode**](V1WorkflowNode.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_init_workflow_node_response import V1InitWorkflowNodeResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1InitWorkflowNodeResponse from a JSON string
v1_init_workflow_node_response_instance = V1InitWorkflowNodeResponse.from_json(json)
# print the JSON string representation of the object
print(V1InitWorkflowNodeResponse.to_json())

# convert the object into a dict
v1_init_workflow_node_response_dict = v1_init_workflow_node_response_instance.to_dict()
# create an instance of V1InitWorkflowNodeResponse from a dict
v1_init_workflow_node_response_from_dict = V1InitWorkflowNodeResponse.from_dict(v1_init_workflow_node_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


