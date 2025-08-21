# V1ListWorkflowsSharedWithMeResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**workflows** | [**List[V1Workflow]**](V1Workflow.md) | The Workflows that match the request. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_list_workflows_shared_with_me_response import V1ListWorkflowsSharedWithMeResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListWorkflowsSharedWithMeResponse from a JSON string
v1_list_workflows_shared_with_me_response_instance = V1ListWorkflowsSharedWithMeResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListWorkflowsSharedWithMeResponse.to_json())

# convert the object into a dict
v1_list_workflows_shared_with_me_response_dict = v1_list_workflows_shared_with_me_response_instance.to_dict()
# create an instance of V1ListWorkflowsSharedWithMeResponse from a dict
v1_list_workflows_shared_with_me_response_from_dict = V1ListWorkflowsSharedWithMeResponse.from_dict(v1_list_workflows_shared_with_me_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


