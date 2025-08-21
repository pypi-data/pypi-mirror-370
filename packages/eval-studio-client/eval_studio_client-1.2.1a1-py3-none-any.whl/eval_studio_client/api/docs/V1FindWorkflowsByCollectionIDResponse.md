# V1FindWorkflowsByCollectionIDResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**workflows** | [**List[V1Workflow]**](V1Workflow.md) | The Workflows found. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_find_workflows_by_collection_id_response import V1FindWorkflowsByCollectionIDResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1FindWorkflowsByCollectionIDResponse from a JSON string
v1_find_workflows_by_collection_id_response_instance = V1FindWorkflowsByCollectionIDResponse.from_json(json)
# print the JSON string representation of the object
print(V1FindWorkflowsByCollectionIDResponse.to_json())

# convert the object into a dict
v1_find_workflows_by_collection_id_response_dict = v1_find_workflows_by_collection_id_response_instance.to_dict()
# create an instance of V1FindWorkflowsByCollectionIDResponse from a dict
v1_find_workflows_by_collection_id_response_from_dict = V1FindWorkflowsByCollectionIDResponse.from_dict(v1_find_workflows_by_collection_id_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


