# V1ListWorkflowAccessResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**role_bindings** | [**List[V1RoleBinding]**](V1RoleBinding.md) | The RoleBindings for the Workflow requested. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_list_workflow_access_response import V1ListWorkflowAccessResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListWorkflowAccessResponse from a JSON string
v1_list_workflow_access_response_instance = V1ListWorkflowAccessResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListWorkflowAccessResponse.to_json())

# convert the object into a dict
v1_list_workflow_access_response_dict = v1_list_workflow_access_response_instance.to_dict()
# create an instance of V1ListWorkflowAccessResponse from a dict
v1_list_workflow_access_response_from_dict = V1ListWorkflowAccessResponse.from_dict(v1_list_workflow_access_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


