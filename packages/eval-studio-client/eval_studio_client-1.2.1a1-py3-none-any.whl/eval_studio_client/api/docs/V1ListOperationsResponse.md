# V1ListOperationsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**operations** | [**List[V1Operation]**](V1Operation.md) | The list of Operations. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_list_operations_response import V1ListOperationsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListOperationsResponse from a JSON string
v1_list_operations_response_instance = V1ListOperationsResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListOperationsResponse.to_json())

# convert the object into a dict
v1_list_operations_response_dict = v1_list_operations_response_instance.to_dict()
# create an instance of V1ListOperationsResponse from a dict
v1_list_operations_response_from_dict = V1ListOperationsResponse.from_dict(v1_list_operations_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


