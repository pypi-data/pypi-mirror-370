# V1BatchDeleteEvaluatorsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**evaluators** | [**List[V1Evaluator]**](V1Evaluator.md) | The deleted Evaluators. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_batch_delete_evaluators_response import V1BatchDeleteEvaluatorsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1BatchDeleteEvaluatorsResponse from a JSON string
v1_batch_delete_evaluators_response_instance = V1BatchDeleteEvaluatorsResponse.from_json(json)
# print the JSON string representation of the object
print(V1BatchDeleteEvaluatorsResponse.to_json())

# convert the object into a dict
v1_batch_delete_evaluators_response_dict = v1_batch_delete_evaluators_response_instance.to_dict()
# create an instance of V1BatchDeleteEvaluatorsResponse from a dict
v1_batch_delete_evaluators_response_from_dict = V1BatchDeleteEvaluatorsResponse.from_dict(v1_batch_delete_evaluators_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


