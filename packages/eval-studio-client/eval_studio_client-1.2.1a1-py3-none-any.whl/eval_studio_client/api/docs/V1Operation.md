# V1Operation

This resource represents a long-running operation that is the result of a network API call.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] [readonly] 
**create_time** | **datetime** | Output only. Timestamp when the Operation was created. | [optional] [readonly] 
**creator** | **str** | Output only. Name of the user or service that requested creation of the Operation. | [optional] [readonly] 
**update_time** | **datetime** | Output only. Optional. Timestamp when the Operation was last updated. | [optional] [readonly] 
**updater** | **str** | Output only. Optional. Name of the user or service that requested update of the Operation. | [optional] [readonly] 
**delete_time** | **datetime** | Output only. Optional. Set when the Operation is deleted. When set Operation should be considered as deleted. | [optional] [readonly] 
**deleter** | **str** | Output only. Optional. Name of the user or service that requested deletion of the Operation. | [optional] [readonly] 
**metadata** | [**ProtobufAny**](ProtobufAny.md) |  | [optional] 
**done** | **bool** | If the value is &#x60;false&#x60;, it means the operation is still in progress. If &#x60;true&#x60;, the operation is completed, and either &#x60;error&#x60; or &#x60;response&#x60; is available. | [optional] 
**error** | [**RpcStatus**](RpcStatus.md) |  | [optional] 
**response** | [**ProtobufAny**](ProtobufAny.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_operation import V1Operation

# TODO update the JSON string below
json = "{}"
# create an instance of V1Operation from a JSON string
v1_operation_instance = V1Operation.from_json(json)
# print the JSON string representation of the object
print(V1Operation.to_json())

# convert the object into a dict
v1_operation_dict = v1_operation_instance.to_dict()
# create an instance of V1Operation from a dict
v1_operation_from_dict = V1Operation.from_dict(v1_operation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


