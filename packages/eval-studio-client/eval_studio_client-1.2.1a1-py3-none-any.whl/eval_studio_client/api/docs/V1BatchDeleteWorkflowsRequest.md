# V1BatchDeleteWorkflowsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**names** | **List[str]** | Required. The names of the Workflows to delete. A maximum of 1000 can be specified. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_batch_delete_workflows_request import V1BatchDeleteWorkflowsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of V1BatchDeleteWorkflowsRequest from a JSON string
v1_batch_delete_workflows_request_instance = V1BatchDeleteWorkflowsRequest.from_json(json)
# print the JSON string representation of the object
print(V1BatchDeleteWorkflowsRequest.to_json())

# convert the object into a dict
v1_batch_delete_workflows_request_dict = v1_batch_delete_workflows_request_instance.to_dict()
# create an instance of V1BatchDeleteWorkflowsRequest from a dict
v1_batch_delete_workflows_request_from_dict = V1BatchDeleteWorkflowsRequest.from_dict(v1_batch_delete_workflows_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


