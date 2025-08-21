# V1ListWorkflowDependenciesResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**nodes** | [**List[V1WorkflowNode]**](V1WorkflowNode.md) | The list of the WorkflowNodes related to requested workflow. | [optional] 
**dependencies** | [**List[V1DependencyList]**](V1DependencyList.md) | The dependency map for the workflow. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_list_workflow_dependencies_response import V1ListWorkflowDependenciesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListWorkflowDependenciesResponse from a JSON string
v1_list_workflow_dependencies_response_instance = V1ListWorkflowDependenciesResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListWorkflowDependenciesResponse.to_json())

# convert the object into a dict
v1_list_workflow_dependencies_response_dict = v1_list_workflow_dependencies_response_instance.to_dict()
# create an instance of V1ListWorkflowDependenciesResponse from a dict
v1_list_workflow_dependencies_response_from_dict = V1ListWorkflowDependenciesResponse.from_dict(v1_list_workflow_dependencies_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


