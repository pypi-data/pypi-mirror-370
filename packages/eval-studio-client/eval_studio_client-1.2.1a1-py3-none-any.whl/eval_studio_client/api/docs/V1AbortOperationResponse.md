# V1AbortOperationResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**operation** | [**V1Operation**](V1Operation.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_abort_operation_response import V1AbortOperationResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1AbortOperationResponse from a JSON string
v1_abort_operation_response_instance = V1AbortOperationResponse.from_json(json)
# print the JSON string representation of the object
print(V1AbortOperationResponse.to_json())

# convert the object into a dict
v1_abort_operation_response_dict = v1_abort_operation_response_instance.to_dict()
# create an instance of V1AbortOperationResponse from a dict
v1_abort_operation_response_from_dict = V1AbortOperationResponse.from_dict(v1_abort_operation_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


