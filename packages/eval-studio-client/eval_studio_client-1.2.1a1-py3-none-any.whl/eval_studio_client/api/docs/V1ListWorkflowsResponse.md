# V1ListWorkflowsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**workflows** | [**List[V1Workflow]**](V1Workflow.md) | The Workflows requested. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_list_workflows_response import V1ListWorkflowsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListWorkflowsResponse from a JSON string
v1_list_workflows_response_instance = V1ListWorkflowsResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListWorkflowsResponse.to_json())

# convert the object into a dict
v1_list_workflows_response_dict = v1_list_workflows_response_instance.to_dict()
# create an instance of V1ListWorkflowsResponse from a dict
v1_list_workflows_response_from_dict = V1ListWorkflowsResponse.from_dict(v1_list_workflows_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


