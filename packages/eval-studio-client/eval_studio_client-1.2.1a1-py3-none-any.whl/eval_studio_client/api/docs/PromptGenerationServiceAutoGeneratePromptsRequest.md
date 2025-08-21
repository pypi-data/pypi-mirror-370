# PromptGenerationServiceAutoGeneratePromptsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**operation** | **str** | Required. The Operation processing this prompt generation process. | [optional] 
**model** | [**V1Model**](V1Model.md) |  | [optional] 
**count** | **int** | Required. The number of TestCases to generate. | [optional] 
**base_llm_model** | **str** | Required. Base LLM model to use for generating the prompts. | [optional] 
**document_urls** | [**V1RepeatedString**](V1RepeatedString.md) |  | [optional] 
**chunks** | [**V1RepeatedContext**](V1RepeatedContext.md) |  | [optional] 
**generators** | [**List[V1TestCasesGenerator]**](V1TestCasesGenerator.md) | Optional. Type of questions to generate TestCases for. If not specified, all types of questions are selected. | [optional] 
**h2ogpte_collection_id** | **str** | Optional. The ID of the h2oGPTe collection to use. If empty, new temporary collection will be created. | [optional] 
**topics** | **List[str]** | Optional. Topics to generate questions for. If not specified, use document summarization as topic generation. | [optional] 

## Example

```python
from eval_studio_client.api.models.prompt_generation_service_auto_generate_prompts_request import PromptGenerationServiceAutoGeneratePromptsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PromptGenerationServiceAutoGeneratePromptsRequest from a JSON string
prompt_generation_service_auto_generate_prompts_request_instance = PromptGenerationServiceAutoGeneratePromptsRequest.from_json(json)
# print the JSON string representation of the object
print(PromptGenerationServiceAutoGeneratePromptsRequest.to_json())

# convert the object into a dict
prompt_generation_service_auto_generate_prompts_request_dict = prompt_generation_service_auto_generate_prompts_request_instance.to_dict()
# create an instance of PromptGenerationServiceAutoGeneratePromptsRequest from a dict
prompt_generation_service_auto_generate_prompts_request_from_dict = PromptGenerationServiceAutoGeneratePromptsRequest.from_dict(prompt_generation_service_auto_generate_prompts_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


