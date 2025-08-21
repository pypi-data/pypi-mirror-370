# V1WorkflowDependency


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Required. The name of the Workflow Dependency node. | [optional] 
**optional** | **bool** | Optional. Whether the dependency is optional. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_workflow_dependency import V1WorkflowDependency

# TODO update the JSON string below
json = "{}"
# create an instance of V1WorkflowDependency from a JSON string
v1_workflow_dependency_instance = V1WorkflowDependency.from_json(json)
# print the JSON string representation of the object
print(V1WorkflowDependency.to_json())

# convert the object into a dict
v1_workflow_dependency_dict = v1_workflow_dependency_instance.to_dict()
# create an instance of V1WorkflowDependency from a dict
v1_workflow_dependency_from_dict = V1WorkflowDependency.from_dict(v1_workflow_dependency_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


