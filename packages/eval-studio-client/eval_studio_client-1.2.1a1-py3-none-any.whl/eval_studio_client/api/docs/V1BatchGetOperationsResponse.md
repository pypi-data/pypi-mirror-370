# V1BatchGetOperationsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**operations** | [**List[V1Operation]**](V1Operation.md) | The Operations that were requested. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_batch_get_operations_response import V1BatchGetOperationsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1BatchGetOperationsResponse from a JSON string
v1_batch_get_operations_response_instance = V1BatchGetOperationsResponse.from_json(json)
# print the JSON string representation of the object
print(V1BatchGetOperationsResponse.to_json())

# convert the object into a dict
v1_batch_get_operations_response_dict = v1_batch_get_operations_response_instance.to_dict()
# create an instance of V1BatchGetOperationsResponse from a dict
v1_batch_get_operations_response_from_dict = V1BatchGetOperationsResponse.from_dict(v1_batch_get_operations_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


