# V1GetOperationProgressByParentResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**operation_progress** | [**V1OperationProgress**](V1OperationProgress.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_get_operation_progress_by_parent_response import V1GetOperationProgressByParentResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1GetOperationProgressByParentResponse from a JSON string
v1_get_operation_progress_by_parent_response_instance = V1GetOperationProgressByParentResponse.from_json(json)
# print the JSON string representation of the object
print(V1GetOperationProgressByParentResponse.to_json())

# convert the object into a dict
v1_get_operation_progress_by_parent_response_dict = v1_get_operation_progress_by_parent_response_instance.to_dict()
# create an instance of V1GetOperationProgressByParentResponse from a dict
v1_get_operation_progress_by_parent_response_from_dict = V1GetOperationProgressByParentResponse.from_dict(v1_get_operation_progress_by_parent_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


