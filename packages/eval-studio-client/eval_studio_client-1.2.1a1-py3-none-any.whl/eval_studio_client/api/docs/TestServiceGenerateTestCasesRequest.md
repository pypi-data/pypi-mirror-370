# TestServiceGenerateTestCasesRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** | Required. The number of TestCases to generate. | [optional] 
**model** | **str** | Optional. The Model to use for generating TestCases. If not specified, the default RAG h2oGPTe will be used. Error is returned, if no default model is specified and this field is not set. | [optional] 
**base_llm_model** | **str** | Optional. The base LLM model to use for generating the prompts. Selected automatically if not specified. | [optional] 
**generators** | [**List[V1TestCasesGenerator]**](V1TestCasesGenerator.md) | Optional. Generators to use for generation. If not specified, all generators are selected. | [optional] 
**h2ogpte_collection_id** | **str** | Optional. ID of the h2oGPTe collection to use. If provided, documents referenced by Test and any specified chunks are ignored. This field is required if Test does not reference any documents and no chunks are provided. If this field is left empty, a temporary collection will be created. | [optional] 
**topics** | **List[str]** | Optional. Topics to generate questions for. If not specified, use document summarization as topic generation. | [optional] 
**chunks** | [**List[V1Context]**](V1Context.md) | Optional. The list of chunks to use for generation. If set, the Documents assigned to the Test and h2ogpte_collection_id are ignored. | [optional] 

## Example

```python
from eval_studio_client.api.models.test_service_generate_test_cases_request import TestServiceGenerateTestCasesRequest

# TODO update the JSON string below
json = "{}"
# create an instance of TestServiceGenerateTestCasesRequest from a JSON string
test_service_generate_test_cases_request_instance = TestServiceGenerateTestCasesRequest.from_json(json)
# print the JSON string representation of the object
print(TestServiceGenerateTestCasesRequest.to_json())

# convert the object into a dict
test_service_generate_test_cases_request_dict = test_service_generate_test_cases_request_instance.to_dict()
# create an instance of TestServiceGenerateTestCasesRequest from a dict
test_service_generate_test_cases_request_from_dict = TestServiceGenerateTestCasesRequest.from_dict(test_service_generate_test_cases_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


