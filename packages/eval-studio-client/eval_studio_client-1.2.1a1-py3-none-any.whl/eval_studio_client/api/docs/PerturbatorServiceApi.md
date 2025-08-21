# eval_studio_client.api.PerturbatorServiceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**perturbator_service_get_perturbator**](PerturbatorServiceApi.md#perturbator_service_get_perturbator) | **GET** /v1/{name_7} | 
[**perturbator_service_list_perturbators**](PerturbatorServiceApi.md#perturbator_service_list_perturbators) | **GET** /v1/perturbators | 


# **perturbator_service_get_perturbator**
> V1GetPerturbatorResponse perturbator_service_get_perturbator(name_7)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_get_perturbator_response import V1GetPerturbatorResponse
from eval_studio_client.api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = eval_studio_client.api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with eval_studio_client.api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = eval_studio_client.api.PerturbatorServiceApi(api_client)
    name_7 = 'name_7_example' # str | Required. The name of the Perturbator to retrieve.

    try:
        api_response = api_instance.perturbator_service_get_perturbator(name_7)
        print("The response of PerturbatorServiceApi->perturbator_service_get_perturbator:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PerturbatorServiceApi->perturbator_service_get_perturbator: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name_7** | **str**| Required. The name of the Perturbator to retrieve. | 

### Return type

[**V1GetPerturbatorResponse**](V1GetPerturbatorResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**0** | An unexpected error response. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **perturbator_service_list_perturbators**
> V1ListPerturbatorsResponse perturbator_service_list_perturbators(default_h2ogpte_model_name=default_h2ogpte_model_name, default_h2ogpte_model_create_time=default_h2ogpte_model_create_time, default_h2ogpte_model_creator=default_h2ogpte_model_creator, default_h2ogpte_model_update_time=default_h2ogpte_model_update_time, default_h2ogpte_model_updater=default_h2ogpte_model_updater, default_h2ogpte_model_delete_time=default_h2ogpte_model_delete_time, default_h2ogpte_model_deleter=default_h2ogpte_model_deleter, default_h2ogpte_model_display_name=default_h2ogpte_model_display_name, default_h2ogpte_model_description=default_h2ogpte_model_description, default_h2ogpte_model_url=default_h2ogpte_model_url, default_h2ogpte_model_api_key=default_h2ogpte_model_api_key, default_h2ogpte_model_type=default_h2ogpte_model_type, default_h2ogpte_model_parameters=default_h2ogpte_model_parameters, default_h2ogpte_model_demo=default_h2ogpte_model_demo)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_list_perturbators_response import V1ListPerturbatorsResponse
from eval_studio_client.api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = eval_studio_client.api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with eval_studio_client.api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = eval_studio_client.api.PerturbatorServiceApi(api_client)
    default_h2ogpte_model_name = 'default_h2ogpte_model_name_example' # str | Output only. Name of the Model resource. e.g.: \"models/<UUID>\" (optional)
    default_h2ogpte_model_create_time = '2013-10-20T19:20:30+01:00' # datetime | Output only. Timestamp when the Model was created. (optional)
    default_h2ogpte_model_creator = 'default_h2ogpte_model_creator_example' # str | Output only. Name of the user or service that requested creation of the Model. (optional)
    default_h2ogpte_model_update_time = '2013-10-20T19:20:30+01:00' # datetime | Output only. Optional. Timestamp when the Model was last updated. (optional)
    default_h2ogpte_model_updater = 'default_h2ogpte_model_updater_example' # str | Output only. Optional. Name of the user or service that requested update of the Model. (optional)
    default_h2ogpte_model_delete_time = '2013-10-20T19:20:30+01:00' # datetime | Output only. Optional. Set when the Model is deleted. When set Model should be considered as deleted. (optional)
    default_h2ogpte_model_deleter = 'default_h2ogpte_model_deleter_example' # str | Output only. Optional. Name of the user or service that requested deletion of the Model. (optional)
    default_h2ogpte_model_display_name = 'default_h2ogpte_model_display_name_example' # str | Human readable name of the Model. (optional)
    default_h2ogpte_model_description = 'default_h2ogpte_model_description_example' # str | Optional. Arbitrary description of the Model. (optional)
    default_h2ogpte_model_url = 'default_h2ogpte_model_url_example' # str | Optional. Immutable. Absolute URL to the Model. (optional)
    default_h2ogpte_model_api_key = 'default_h2ogpte_model_api_key_example' # str | Optional. API key used to access the Model. Not set for read calls (i.e. get, list) by public clients (front-end). Set only for internal (server-to-worker) communication. (optional)
    default_h2ogpte_model_type = 'MODEL_TYPE_UNSPECIFIED' # str | Immutable. Type of this Model.   - MODEL_TYPE_UNSPECIFIED: Unspecified type.  - MODEL_TYPE_H2OGPTE_RAG: h2oGPTe RAG.  - MODEL_TYPE_OPENAI_RAG: OpenAI Assistant RAG.  - MODEL_TYPE_H2OGPTE_LLM: h2oGPTe LLM.  - MODEL_TYPE_H2OGPT_LLM: h2oGPT LLM.  - MODEL_TYPE_OPENAI_CHAT: OpenAI chat.  - MODEL_TYPE_AZURE_OPENAI_CHAT: Microsoft Azure hosted OpenAI Chat.  - MODEL_TYPE_OPENAI_API_CHAT: OpenAI API chat.  - MODEL_TYPE_H2OLLMOPS: H2O LLMOps.  - MODEL_TYPE_OLLAMA: Ollama.  - MODEL_TYPE_AMAZON_BEDROCK: Amazon Bedrock. (optional) (default to 'MODEL_TYPE_UNSPECIFIED')
    default_h2ogpte_model_parameters = 'default_h2ogpte_model_parameters_example' # str | Optional. Model specific parameters in JSON format. (optional)
    default_h2ogpte_model_demo = True # bool | Output only. Whether the Model is a demo resource or not. Demo resources are read only. (optional)

    try:
        api_response = api_instance.perturbator_service_list_perturbators(default_h2ogpte_model_name=default_h2ogpte_model_name, default_h2ogpte_model_create_time=default_h2ogpte_model_create_time, default_h2ogpte_model_creator=default_h2ogpte_model_creator, default_h2ogpte_model_update_time=default_h2ogpte_model_update_time, default_h2ogpte_model_updater=default_h2ogpte_model_updater, default_h2ogpte_model_delete_time=default_h2ogpte_model_delete_time, default_h2ogpte_model_deleter=default_h2ogpte_model_deleter, default_h2ogpte_model_display_name=default_h2ogpte_model_display_name, default_h2ogpte_model_description=default_h2ogpte_model_description, default_h2ogpte_model_url=default_h2ogpte_model_url, default_h2ogpte_model_api_key=default_h2ogpte_model_api_key, default_h2ogpte_model_type=default_h2ogpte_model_type, default_h2ogpte_model_parameters=default_h2ogpte_model_parameters, default_h2ogpte_model_demo=default_h2ogpte_model_demo)
        print("The response of PerturbatorServiceApi->perturbator_service_list_perturbators:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PerturbatorServiceApi->perturbator_service_list_perturbators: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **default_h2ogpte_model_name** | **str**| Output only. Name of the Model resource. e.g.: \&quot;models/&lt;UUID&gt;\&quot; | [optional] 
 **default_h2ogpte_model_create_time** | **datetime**| Output only. Timestamp when the Model was created. | [optional] 
 **default_h2ogpte_model_creator** | **str**| Output only. Name of the user or service that requested creation of the Model. | [optional] 
 **default_h2ogpte_model_update_time** | **datetime**| Output only. Optional. Timestamp when the Model was last updated. | [optional] 
 **default_h2ogpte_model_updater** | **str**| Output only. Optional. Name of the user or service that requested update of the Model. | [optional] 
 **default_h2ogpte_model_delete_time** | **datetime**| Output only. Optional. Set when the Model is deleted. When set Model should be considered as deleted. | [optional] 
 **default_h2ogpte_model_deleter** | **str**| Output only. Optional. Name of the user or service that requested deletion of the Model. | [optional] 
 **default_h2ogpte_model_display_name** | **str**| Human readable name of the Model. | [optional] 
 **default_h2ogpte_model_description** | **str**| Optional. Arbitrary description of the Model. | [optional] 
 **default_h2ogpte_model_url** | **str**| Optional. Immutable. Absolute URL to the Model. | [optional] 
 **default_h2ogpte_model_api_key** | **str**| Optional. API key used to access the Model. Not set for read calls (i.e. get, list) by public clients (front-end). Set only for internal (server-to-worker) communication. | [optional] 
 **default_h2ogpte_model_type** | **str**| Immutable. Type of this Model.   - MODEL_TYPE_UNSPECIFIED: Unspecified type.  - MODEL_TYPE_H2OGPTE_RAG: h2oGPTe RAG.  - MODEL_TYPE_OPENAI_RAG: OpenAI Assistant RAG.  - MODEL_TYPE_H2OGPTE_LLM: h2oGPTe LLM.  - MODEL_TYPE_H2OGPT_LLM: h2oGPT LLM.  - MODEL_TYPE_OPENAI_CHAT: OpenAI chat.  - MODEL_TYPE_AZURE_OPENAI_CHAT: Microsoft Azure hosted OpenAI Chat.  - MODEL_TYPE_OPENAI_API_CHAT: OpenAI API chat.  - MODEL_TYPE_H2OLLMOPS: H2O LLMOps.  - MODEL_TYPE_OLLAMA: Ollama.  - MODEL_TYPE_AMAZON_BEDROCK: Amazon Bedrock. | [optional] [default to &#39;MODEL_TYPE_UNSPECIFIED&#39;]
 **default_h2ogpte_model_parameters** | **str**| Optional. Model specific parameters in JSON format. | [optional] 
 **default_h2ogpte_model_demo** | **bool**| Output only. Whether the Model is a demo resource or not. Demo resources are read only. | [optional] 

### Return type

[**V1ListPerturbatorsResponse**](V1ListPerturbatorsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**0** | An unexpected error response. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

