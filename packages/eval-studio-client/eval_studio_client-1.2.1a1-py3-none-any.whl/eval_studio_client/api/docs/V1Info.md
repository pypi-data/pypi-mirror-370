# V1Info


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**base_url** | **str** | The base absolute URL of the Eval Studio instance. | [optional] 
**version** | **str** | The version of the Eval Studio instance. | [optional] 
**oauth2_login_url** | **str** | The URL for initiating the OAuth2 flow. | [optional] 
**oauth2_logout_url** | **str** | The URL for logging out. | [optional] 
**h2o_gpte_allowlist** | **List[str]** | Allowlist of H2OGPTe models for UI that can be used in Eval Studio. E.g. gpt-35-turbo-1106, h2oai/h2ogpt-4096-llama2-13b-chat, h2oai/h2ogpt-4096-llama2-70b-chat-4bit, HuggingFaceH4/zephyr-7b-beta, h2oai/h2ogpt-gm-7b-mistral-chat-sft-dpo-v1, h2oai/h2ogpt-gm-experimental. | [optional] 
**h2o_gpte_client_version** | **str** | The version of h2oGPTe client used by the workers. | [optional] 
**h2o_sonar_version** | **str** | The version of H2O Sonar used by the workers. | [optional] 
**preferred_llms_for_test_generation** | **List[str]** | Ordered list of LLMs preferred for test generation. The value might be a regular expression. | [optional] 
**h2o_cloud_url** | **str** | The URL for the H2O Cloud host. | [optional] 
**public_instance** | **bool** | If the Eval Studio instance is public. | [optional] 
**sharing_enabled** | **bool** | Whether the sharing capability is enabled. | [optional] 
**experimental_features_enabled** | **bool** | Whether the experimental features are enabled. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_info import V1Info

# TODO update the JSON string below
json = "{}"
# create an instance of V1Info from a JSON string
v1_info_instance = V1Info.from_json(json)
# print the JSON string representation of the object
print(V1Info.to_json())

# convert the object into a dict
v1_info_dict = v1_info_instance.to_dict()
# create an instance of V1Info from a dict
v1_info_from_dict = V1Info.from_dict(v1_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


