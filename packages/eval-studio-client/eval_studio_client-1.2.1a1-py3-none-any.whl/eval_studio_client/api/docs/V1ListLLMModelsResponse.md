# V1ListLLMModelsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**models** | **List[str]** | Required. List of LLM models available for evaluation. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_list_llm_models_response import V1ListLLMModelsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListLLMModelsResponse from a JSON string
v1_list_llm_models_response_instance = V1ListLLMModelsResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListLLMModelsResponse.to_json())

# convert the object into a dict
v1_list_llm_models_response_dict = v1_list_llm_models_response_instance.to_dict()
# create an instance of V1ListLLMModelsResponse from a dict
v1_list_llm_models_response_from_dict = V1ListLLMModelsResponse.from_dict(v1_list_llm_models_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


