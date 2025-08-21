# V1GetWorkflowNodePrerequisitesResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**nodes** | **List[str]** | The WorkflowNodes that are the prerequisites of the specified WorkflowNode. | [optional] 
**edges** | **List[str]** | The WorkflowEdges that are the prerequisites of the specified WorkflowNode. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_get_workflow_node_prerequisites_response import V1GetWorkflowNodePrerequisitesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1GetWorkflowNodePrerequisitesResponse from a JSON string
v1_get_workflow_node_prerequisites_response_instance = V1GetWorkflowNodePrerequisitesResponse.from_json(json)
# print the JSON string representation of the object
print(V1GetWorkflowNodePrerequisitesResponse.to_json())

# convert the object into a dict
v1_get_workflow_node_prerequisites_response_dict = v1_get_workflow_node_prerequisites_response_instance.to_dict()
# create an instance of V1GetWorkflowNodePrerequisitesResponse from a dict
v1_get_workflow_node_prerequisites_response_from_dict = V1GetWorkflowNodePrerequisitesResponse.from_dict(v1_get_workflow_node_prerequisites_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


