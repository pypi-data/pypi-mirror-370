# V1BatchDeleteWorkflowsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**workflows** | [**List[V1Workflow]**](V1Workflow.md) | The deleted Workflows. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_batch_delete_workflows_response import V1BatchDeleteWorkflowsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1BatchDeleteWorkflowsResponse from a JSON string
v1_batch_delete_workflows_response_instance = V1BatchDeleteWorkflowsResponse.from_json(json)
# print the JSON string representation of the object
print(V1BatchDeleteWorkflowsResponse.to_json())

# convert the object into a dict
v1_batch_delete_workflows_response_dict = v1_batch_delete_workflows_response_instance.to_dict()
# create an instance of V1BatchDeleteWorkflowsResponse from a dict
v1_batch_delete_workflows_response_from_dict = V1BatchDeleteWorkflowsResponse.from_dict(v1_batch_delete_workflows_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


