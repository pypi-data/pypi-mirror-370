# V1WorkflowNodeArtifacts


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**artifacts** | [**List[V1WorkflowNodeArtifact]**](V1WorkflowNodeArtifact.md) | Output only. List of the WorkflowNodeArtifacts produced by the WorkflowNode. | [optional] [readonly] 

## Example

```python
from eval_studio_client.api.models.v1_workflow_node_artifacts import V1WorkflowNodeArtifacts

# TODO update the JSON string below
json = "{}"
# create an instance of V1WorkflowNodeArtifacts from a JSON string
v1_workflow_node_artifacts_instance = V1WorkflowNodeArtifacts.from_json(json)
# print the JSON string representation of the object
print(V1WorkflowNodeArtifacts.to_json())

# convert the object into a dict
v1_workflow_node_artifacts_dict = v1_workflow_node_artifacts_instance.to_dict()
# create an instance of V1WorkflowNodeArtifacts from a dict
v1_workflow_node_artifacts_from_dict = V1WorkflowNodeArtifacts.from_dict(v1_workflow_node_artifacts_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


