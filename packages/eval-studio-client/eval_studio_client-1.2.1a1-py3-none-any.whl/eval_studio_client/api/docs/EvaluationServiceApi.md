# eval_studio_client.api.EvaluationServiceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**evaluation_service_create_evaluation**](EvaluationServiceApi.md#evaluation_service_create_evaluation) | **POST** /v1/evaluations | 
[**evaluation_service_import_evaluation**](EvaluationServiceApi.md#evaluation_service_import_evaluation) | **POST** /v1/evaluations:import | 
[**evaluation_service_list_llm_models**](EvaluationServiceApi.md#evaluation_service_list_llm_models) | **GET** /v1/evaluations:llm_models | 
[**evaluation_service_list_rag_collections**](EvaluationServiceApi.md#evaluation_service_list_rag_collections) | **GET** /v1/evaluations:rag_collections | 


# **evaluation_service_create_evaluation**
> V1Operation evaluation_service_create_evaluation(body)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_create_evaluation_request import V1CreateEvaluationRequest
from eval_studio_client.api.models.v1_operation import V1Operation
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
    api_instance = eval_studio_client.api.EvaluationServiceApi(api_client)
    body = eval_studio_client.api.V1CreateEvaluationRequest() # V1CreateEvaluationRequest | 

    try:
        api_response = api_instance.evaluation_service_create_evaluation(body)
        print("The response of EvaluationServiceApi->evaluation_service_create_evaluation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EvaluationServiceApi->evaluation_service_create_evaluation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**V1CreateEvaluationRequest**](V1CreateEvaluationRequest.md)|  | 

### Return type

[**V1Operation**](V1Operation.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**0** | An unexpected error response. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **evaluation_service_import_evaluation**
> V1Operation evaluation_service_import_evaluation(body)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_import_evaluation_request import V1ImportEvaluationRequest
from eval_studio_client.api.models.v1_operation import V1Operation
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
    api_instance = eval_studio_client.api.EvaluationServiceApi(api_client)
    body = eval_studio_client.api.V1ImportEvaluationRequest() # V1ImportEvaluationRequest | 

    try:
        api_response = api_instance.evaluation_service_import_evaluation(body)
        print("The response of EvaluationServiceApi->evaluation_service_import_evaluation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EvaluationServiceApi->evaluation_service_import_evaluation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**V1ImportEvaluationRequest**](V1ImportEvaluationRequest.md)|  | 

### Return type

[**V1Operation**](V1Operation.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A successful response. |  -  |
**0** | An unexpected error response. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **evaluation_service_list_llm_models**
> V1ListLLMModelsResponse evaluation_service_list_llm_models(model_name=model_name, model_create_time=model_create_time, model_creator=model_creator, model_update_time=model_update_time, model_updater=model_updater, model_delete_time=model_delete_time, model_deleter=model_deleter, model_display_name=model_display_name, model_description=model_description, model_url=model_url, model_api_key=model_api_key, model_type=model_type, model_parameters=model_parameters, model_demo=model_demo, retries=retries)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_list_llm_models_response import V1ListLLMModelsResponse
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
    api_instance = eval_studio_client.api.EvaluationServiceApi(api_client)
    model_name = 'model_name_example' # str | Output only. Name of the Model resource. e.g.: \"models/<UUID>\" (optional)
    model_create_time = '2013-10-20T19:20:30+01:00' # datetime | Output only. Timestamp when the Model was created. (optional)
    model_creator = 'model_creator_example' # str | Output only. Name of the user or service that requested creation of the Model. (optional)
    model_update_time = '2013-10-20T19:20:30+01:00' # datetime | Output only. Optional. Timestamp when the Model was last updated. (optional)
    model_updater = 'model_updater_example' # str | Output only. Optional. Name of the user or service that requested update of the Model. (optional)
    model_delete_time = '2013-10-20T19:20:30+01:00' # datetime | Output only. Optional. Set when the Model is deleted. When set Model should be considered as deleted. (optional)
    model_deleter = 'model_deleter_example' # str | Output only. Optional. Name of the user or service that requested deletion of the Model. (optional)
    model_display_name = 'model_display_name_example' # str | Human readable name of the Model. (optional)
    model_description = 'model_description_example' # str | Optional. Arbitrary description of the Model. (optional)
    model_url = 'model_url_example' # str | Optional. Immutable. Absolute URL to the Model. (optional)
    model_api_key = 'model_api_key_example' # str | Optional. API key used to access the Model. Not set for read calls (i.e. get, list) by public clients (front-end). Set only for internal (server-to-worker) communication. (optional)
    model_type = 'MODEL_TYPE_UNSPECIFIED' # str | Immutable. Type of this Model.   - MODEL_TYPE_UNSPECIFIED: Unspecified type.  - MODEL_TYPE_H2OGPTE_RAG: h2oGPTe RAG.  - MODEL_TYPE_OPENAI_RAG: OpenAI Assistant RAG.  - MODEL_TYPE_H2OGPTE_LLM: h2oGPTe LLM.  - MODEL_TYPE_H2OGPT_LLM: h2oGPT LLM.  - MODEL_TYPE_OPENAI_CHAT: OpenAI chat.  - MODEL_TYPE_AZURE_OPENAI_CHAT: Microsoft Azure hosted OpenAI Chat.  - MODEL_TYPE_OPENAI_API_CHAT: OpenAI API chat.  - MODEL_TYPE_H2OLLMOPS: H2O LLMOps.  - MODEL_TYPE_OLLAMA: Ollama.  - MODEL_TYPE_AMAZON_BEDROCK: Amazon Bedrock. (optional) (default to 'MODEL_TYPE_UNSPECIFIED')
    model_parameters = 'model_parameters_example' # str | Optional. Model specific parameters in JSON format. (optional)
    model_demo = True # bool | Output only. Whether the Model is a demo resource or not. Demo resources are read only. (optional)
    retries = 56 # int | Optional. The number of retries to attempt when querying the model for available LLM models. Defaults to 5. (optional)

    try:
        api_response = api_instance.evaluation_service_list_llm_models(model_name=model_name, model_create_time=model_create_time, model_creator=model_creator, model_update_time=model_update_time, model_updater=model_updater, model_delete_time=model_delete_time, model_deleter=model_deleter, model_display_name=model_display_name, model_description=model_description, model_url=model_url, model_api_key=model_api_key, model_type=model_type, model_parameters=model_parameters, model_demo=model_demo, retries=retries)
        print("The response of EvaluationServiceApi->evaluation_service_list_llm_models:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EvaluationServiceApi->evaluation_service_list_llm_models: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_name** | **str**| Output only. Name of the Model resource. e.g.: \&quot;models/&lt;UUID&gt;\&quot; | [optional] 
 **model_create_time** | **datetime**| Output only. Timestamp when the Model was created. | [optional] 
 **model_creator** | **str**| Output only. Name of the user or service that requested creation of the Model. | [optional] 
 **model_update_time** | **datetime**| Output only. Optional. Timestamp when the Model was last updated. | [optional] 
 **model_updater** | **str**| Output only. Optional. Name of the user or service that requested update of the Model. | [optional] 
 **model_delete_time** | **datetime**| Output only. Optional. Set when the Model is deleted. When set Model should be considered as deleted. | [optional] 
 **model_deleter** | **str**| Output only. Optional. Name of the user or service that requested deletion of the Model. | [optional] 
 **model_display_name** | **str**| Human readable name of the Model. | [optional] 
 **model_description** | **str**| Optional. Arbitrary description of the Model. | [optional] 
 **model_url** | **str**| Optional. Immutable. Absolute URL to the Model. | [optional] 
 **model_api_key** | **str**| Optional. API key used to access the Model. Not set for read calls (i.e. get, list) by public clients (front-end). Set only for internal (server-to-worker) communication. | [optional] 
 **model_type** | **str**| Immutable. Type of this Model.   - MODEL_TYPE_UNSPECIFIED: Unspecified type.  - MODEL_TYPE_H2OGPTE_RAG: h2oGPTe RAG.  - MODEL_TYPE_OPENAI_RAG: OpenAI Assistant RAG.  - MODEL_TYPE_H2OGPTE_LLM: h2oGPTe LLM.  - MODEL_TYPE_H2OGPT_LLM: h2oGPT LLM.  - MODEL_TYPE_OPENAI_CHAT: OpenAI chat.  - MODEL_TYPE_AZURE_OPENAI_CHAT: Microsoft Azure hosted OpenAI Chat.  - MODEL_TYPE_OPENAI_API_CHAT: OpenAI API chat.  - MODEL_TYPE_H2OLLMOPS: H2O LLMOps.  - MODEL_TYPE_OLLAMA: Ollama.  - MODEL_TYPE_AMAZON_BEDROCK: Amazon Bedrock. | [optional] [default to &#39;MODEL_TYPE_UNSPECIFIED&#39;]
 **model_parameters** | **str**| Optional. Model specific parameters in JSON format. | [optional] 
 **model_demo** | **bool**| Output only. Whether the Model is a demo resource or not. Demo resources are read only. | [optional] 
 **retries** | **int**| Optional. The number of retries to attempt when querying the model for available LLM models. Defaults to 5. | [optional] 

### Return type

[**V1ListLLMModelsResponse**](V1ListLLMModelsResponse.md)

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

# **evaluation_service_list_rag_collections**
> V1ListRAGCollectionsResponse evaluation_service_list_rag_collections(model_name=model_name, model_create_time=model_create_time, model_creator=model_creator, model_update_time=model_update_time, model_updater=model_updater, model_delete_time=model_delete_time, model_deleter=model_deleter, model_display_name=model_display_name, model_description=model_description, model_url=model_url, model_api_key=model_api_key, model_type=model_type, model_parameters=model_parameters, model_demo=model_demo)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_list_rag_collections_response import V1ListRAGCollectionsResponse
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
    api_instance = eval_studio_client.api.EvaluationServiceApi(api_client)
    model_name = 'model_name_example' # str | Output only. Name of the Model resource. e.g.: \"models/<UUID>\" (optional)
    model_create_time = '2013-10-20T19:20:30+01:00' # datetime | Output only. Timestamp when the Model was created. (optional)
    model_creator = 'model_creator_example' # str | Output only. Name of the user or service that requested creation of the Model. (optional)
    model_update_time = '2013-10-20T19:20:30+01:00' # datetime | Output only. Optional. Timestamp when the Model was last updated. (optional)
    model_updater = 'model_updater_example' # str | Output only. Optional. Name of the user or service that requested update of the Model. (optional)
    model_delete_time = '2013-10-20T19:20:30+01:00' # datetime | Output only. Optional. Set when the Model is deleted. When set Model should be considered as deleted. (optional)
    model_deleter = 'model_deleter_example' # str | Output only. Optional. Name of the user or service that requested deletion of the Model. (optional)
    model_display_name = 'model_display_name_example' # str | Human readable name of the Model. (optional)
    model_description = 'model_description_example' # str | Optional. Arbitrary description of the Model. (optional)
    model_url = 'model_url_example' # str | Optional. Immutable. Absolute URL to the Model. (optional)
    model_api_key = 'model_api_key_example' # str | Optional. API key used to access the Model. Not set for read calls (i.e. get, list) by public clients (front-end). Set only for internal (server-to-worker) communication. (optional)
    model_type = 'MODEL_TYPE_UNSPECIFIED' # str | Immutable. Type of this Model.   - MODEL_TYPE_UNSPECIFIED: Unspecified type.  - MODEL_TYPE_H2OGPTE_RAG: h2oGPTe RAG.  - MODEL_TYPE_OPENAI_RAG: OpenAI Assistant RAG.  - MODEL_TYPE_H2OGPTE_LLM: h2oGPTe LLM.  - MODEL_TYPE_H2OGPT_LLM: h2oGPT LLM.  - MODEL_TYPE_OPENAI_CHAT: OpenAI chat.  - MODEL_TYPE_AZURE_OPENAI_CHAT: Microsoft Azure hosted OpenAI Chat.  - MODEL_TYPE_OPENAI_API_CHAT: OpenAI API chat.  - MODEL_TYPE_H2OLLMOPS: H2O LLMOps.  - MODEL_TYPE_OLLAMA: Ollama.  - MODEL_TYPE_AMAZON_BEDROCK: Amazon Bedrock. (optional) (default to 'MODEL_TYPE_UNSPECIFIED')
    model_parameters = 'model_parameters_example' # str | Optional. Model specific parameters in JSON format. (optional)
    model_demo = True # bool | Output only. Whether the Model is a demo resource or not. Demo resources are read only. (optional)

    try:
        api_response = api_instance.evaluation_service_list_rag_collections(model_name=model_name, model_create_time=model_create_time, model_creator=model_creator, model_update_time=model_update_time, model_updater=model_updater, model_delete_time=model_delete_time, model_deleter=model_deleter, model_display_name=model_display_name, model_description=model_description, model_url=model_url, model_api_key=model_api_key, model_type=model_type, model_parameters=model_parameters, model_demo=model_demo)
        print("The response of EvaluationServiceApi->evaluation_service_list_rag_collections:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EvaluationServiceApi->evaluation_service_list_rag_collections: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model_name** | **str**| Output only. Name of the Model resource. e.g.: \&quot;models/&lt;UUID&gt;\&quot; | [optional] 
 **model_create_time** | **datetime**| Output only. Timestamp when the Model was created. | [optional] 
 **model_creator** | **str**| Output only. Name of the user or service that requested creation of the Model. | [optional] 
 **model_update_time** | **datetime**| Output only. Optional. Timestamp when the Model was last updated. | [optional] 
 **model_updater** | **str**| Output only. Optional. Name of the user or service that requested update of the Model. | [optional] 
 **model_delete_time** | **datetime**| Output only. Optional. Set when the Model is deleted. When set Model should be considered as deleted. | [optional] 
 **model_deleter** | **str**| Output only. Optional. Name of the user or service that requested deletion of the Model. | [optional] 
 **model_display_name** | **str**| Human readable name of the Model. | [optional] 
 **model_description** | **str**| Optional. Arbitrary description of the Model. | [optional] 
 **model_url** | **str**| Optional. Immutable. Absolute URL to the Model. | [optional] 
 **model_api_key** | **str**| Optional. API key used to access the Model. Not set for read calls (i.e. get, list) by public clients (front-end). Set only for internal (server-to-worker) communication. | [optional] 
 **model_type** | **str**| Immutable. Type of this Model.   - MODEL_TYPE_UNSPECIFIED: Unspecified type.  - MODEL_TYPE_H2OGPTE_RAG: h2oGPTe RAG.  - MODEL_TYPE_OPENAI_RAG: OpenAI Assistant RAG.  - MODEL_TYPE_H2OGPTE_LLM: h2oGPTe LLM.  - MODEL_TYPE_H2OGPT_LLM: h2oGPT LLM.  - MODEL_TYPE_OPENAI_CHAT: OpenAI chat.  - MODEL_TYPE_AZURE_OPENAI_CHAT: Microsoft Azure hosted OpenAI Chat.  - MODEL_TYPE_OPENAI_API_CHAT: OpenAI API chat.  - MODEL_TYPE_H2OLLMOPS: H2O LLMOps.  - MODEL_TYPE_OLLAMA: Ollama.  - MODEL_TYPE_AMAZON_BEDROCK: Amazon Bedrock. | [optional] [default to &#39;MODEL_TYPE_UNSPECIFIED&#39;]
 **model_parameters** | **str**| Optional. Model specific parameters in JSON format. | [optional] 
 **model_demo** | **bool**| Output only. Whether the Model is a demo resource or not. Demo resources are read only. | [optional] 

### Return type

[**V1ListRAGCollectionsResponse**](V1ListRAGCollectionsResponse.md)

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

