# V1BatchDeleteEvaluatorsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**names** | **List[str]** | Required. The names of the Evaluators to delete. A maximum of 1000 can be specified. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_batch_delete_evaluators_request import V1BatchDeleteEvaluatorsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of V1BatchDeleteEvaluatorsRequest from a JSON string
v1_batch_delete_evaluators_request_instance = V1BatchDeleteEvaluatorsRequest.from_json(json)
# print the JSON string representation of the object
print(V1BatchDeleteEvaluatorsRequest.to_json())

# convert the object into a dict
v1_batch_delete_evaluators_request_dict = v1_batch_delete_evaluators_request_instance.to_dict()
# create an instance of V1BatchDeleteEvaluatorsRequest from a dict
v1_batch_delete_evaluators_request_from_dict = V1BatchDeleteEvaluatorsRequest.from_dict(v1_batch_delete_evaluators_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


