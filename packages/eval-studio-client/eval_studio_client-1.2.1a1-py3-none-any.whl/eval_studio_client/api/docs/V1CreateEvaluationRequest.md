# V1CreateEvaluationRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**evaluator_identifiers** | **List[str]** | Required. Evaluator identifiers to use, not the resource names. | [optional] 
**model** | [**V1Model**](V1Model.md) |  | [optional] 
**evaluation_tests** | [**List[V1EvaluationTest]**](V1EvaluationTest.md) | TODO: breaks https://google.aip.dev/144 Required. Defines the evaluation configuration. | [optional] 
**operation** | **str** | Required. Resource name of the long-running operation. | [optional] 
**llm_models** | **List[str]** | Optional. If specified, the evaluation will be run on the specified LLM models. If empty, the evaluation will be run on all available LLM models. | [optional] 
**use_cache** | **bool** | Optional. If true, the evaluation will use the TestLab cache, if available, to speedup the evaluation. | [optional] 
**evaluators_parameters** | **Dict[str, str]** | Optional. Additional evaluators configuration, for all the evaluators used in the evaluation. Key is the evaluator identifier, and the value is a JSON string containing the configuration dictionary. | [optional] 
**model_parameters** | **str** | Optional. Parameters overrides in JSON format. | [optional] 
**h2ogpte_collection** | **str** | The existing collection name in H2OGPTe. | [optional] 
**default_h2ogpte_model** | [**V1Model**](V1Model.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_create_evaluation_request import V1CreateEvaluationRequest

# TODO update the JSON string below
json = "{}"
# create an instance of V1CreateEvaluationRequest from a JSON string
v1_create_evaluation_request_instance = V1CreateEvaluationRequest.from_json(json)
# print the JSON string representation of the object
print(V1CreateEvaluationRequest.to_json())

# convert the object into a dict
v1_create_evaluation_request_dict = v1_create_evaluation_request_instance.to_dict()
# create an instance of V1CreateEvaluationRequest from a dict
v1_create_evaluation_request_from_dict = V1CreateEvaluationRequest.from_dict(v1_create_evaluation_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


