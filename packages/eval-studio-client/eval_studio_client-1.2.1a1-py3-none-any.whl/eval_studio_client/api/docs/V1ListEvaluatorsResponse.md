# V1ListEvaluatorsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**evaluators** | [**List[V1Evaluator]**](V1Evaluator.md) | The list of Evaluators. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_list_evaluators_response import V1ListEvaluatorsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListEvaluatorsResponse from a JSON string
v1_list_evaluators_response_instance = V1ListEvaluatorsResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListEvaluatorsResponse.to_json())

# convert the object into a dict
v1_list_evaluators_response_dict = v1_list_evaluators_response_instance.to_dict()
# create an instance of V1ListEvaluatorsResponse from a dict
v1_list_evaluators_response_from_dict = V1ListEvaluatorsResponse.from_dict(v1_list_evaluators_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


