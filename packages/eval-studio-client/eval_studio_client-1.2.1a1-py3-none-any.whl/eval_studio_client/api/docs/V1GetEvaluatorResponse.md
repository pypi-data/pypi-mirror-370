# V1GetEvaluatorResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**evaluator** | [**V1Evaluator**](V1Evaluator.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_get_evaluator_response import V1GetEvaluatorResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1GetEvaluatorResponse from a JSON string
v1_get_evaluator_response_instance = V1GetEvaluatorResponse.from_json(json)
# print the JSON string representation of the object
print(V1GetEvaluatorResponse.to_json())

# convert the object into a dict
v1_get_evaluator_response_dict = v1_get_evaluator_response_instance.to_dict()
# create an instance of V1GetEvaluatorResponse from a dict
v1_get_evaluator_response_from_dict = V1GetEvaluatorResponse.from_dict(v1_get_evaluator_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


