# WorkflowServiceRevokeWorkflowAccessRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**subject** | **str** | Required. The subject to revoke access from. | [optional] 
**role** | [**V1Role**](V1Role.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.workflow_service_revoke_workflow_access_request import WorkflowServiceRevokeWorkflowAccessRequest

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowServiceRevokeWorkflowAccessRequest from a JSON string
workflow_service_revoke_workflow_access_request_instance = WorkflowServiceRevokeWorkflowAccessRequest.from_json(json)
# print the JSON string representation of the object
print(WorkflowServiceRevokeWorkflowAccessRequest.to_json())

# convert the object into a dict
workflow_service_revoke_workflow_access_request_dict = workflow_service_revoke_workflow_access_request_instance.to_dict()
# create an instance of WorkflowServiceRevokeWorkflowAccessRequest from a dict
workflow_service_revoke_workflow_access_request_from_dict = WorkflowServiceRevokeWorkflowAccessRequest.from_dict(workflow_service_revoke_workflow_access_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


