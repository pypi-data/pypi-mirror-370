# AdversarialInputsServiceTestAdversarialInputsRobustnessRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**operation** | **str** | Required. The Operation processing adversarial inputs robustness testing. | [optional] 
**generator_input_types** | [**List[V1TestCasesGenerator]**](V1TestCasesGenerator.md) | Optional. The list of adversarial input types to generate. | [optional] 
**generator_document_urls** | **List[str]** | Required. The document URLs which were used to generate the baseline TestCases. | [optional] 
**generator_model** | [**V1Model**](V1Model.md) |  | [optional] 
**generator_base_llm_model** | **str** | Required. Base LLM model to use for generation of adversarial the prompts. | [optional] 
**generator_count** | **int** | Required. The number of adversarial TestCases to generate. | [optional] 
**generator_topics** | **List[str]** | Optional. Topics to generate questions for. If not specified, use document summarization as topic generation. | [optional] 
**generator_chunks** | **List[str]** | Optional. The list of chunks to use for generation. If set, the Documents assigned to the Test and h2ogpte_collection_id are ignored. | [optional] 
**generator_h2ogpte_collection_id** | **str** | Optional. ID of the h2oGPTe collection to use. If provided, documents referenced by Test and any specified chunks are ignored. This field is required if Test does not reference any documents and no chunks are provided. If this field is left empty, a temporary collection will be created. | [optional] 
**evaluator_identifiers** | **List[str]** | Required. Evaluator identifiers to use for the model evaluation using the adversarial inputs. | [optional] 
**evaluators_parameters** | **Dict[str, str]** | Optional. Additional evaluators configuration, for all the evaluators used in the evaluation. Key is the evaluator identifier, and the value is a JSON string containing the configuration dictionary. | [optional] 
**model** | [**V1Model**](V1Model.md) |  | [optional] 
**base_llm_model** | **str** | Required. Base LLM model to be evaluated using the adversarial inputs. | [optional] 
**model_parameters** | **str** | Optional. Parameters overrides for the Model host in JSON format. | [optional] 
**default_h2ogpte_model** | [**V1Model**](V1Model.md) |  | [optional] 
**baseline_eval** | **str** | Required. Baseline evaluation name. | [optional] 
**baseline_metrics** | [**Dict[str, V1MetricScores]**](V1MetricScores.md) | Required. Map of baseline metrics from the evaluator to the metric scores for the evaluator. | [optional] 

## Example

```python
from eval_studio_client.api.models.adversarial_inputs_service_test_adversarial_inputs_robustness_request import AdversarialInputsServiceTestAdversarialInputsRobustnessRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AdversarialInputsServiceTestAdversarialInputsRobustnessRequest from a JSON string
adversarial_inputs_service_test_adversarial_inputs_robustness_request_instance = AdversarialInputsServiceTestAdversarialInputsRobustnessRequest.from_json(json)
# print the JSON string representation of the object
print(AdversarialInputsServiceTestAdversarialInputsRobustnessRequest.to_json())

# convert the object into a dict
adversarial_inputs_service_test_adversarial_inputs_robustness_request_dict = adversarial_inputs_service_test_adversarial_inputs_robustness_request_instance.to_dict()
# create an instance of AdversarialInputsServiceTestAdversarialInputsRobustnessRequest from a dict
adversarial_inputs_service_test_adversarial_inputs_robustness_request_from_dict = AdversarialInputsServiceTestAdversarialInputsRobustnessRequest.from_dict(adversarial_inputs_service_test_adversarial_inputs_robustness_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


