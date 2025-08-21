# eval_studio_client.api.TestLabServiceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**test_lab_service_create_test_lab**](TestLabServiceApi.md#test_lab_service_create_test_lab) | **POST** /v1/testLabs | 
[**test_lab_service_find_test_lab**](TestLabServiceApi.md#test_lab_service_find_test_lab) | **GET** /v1/testLabs:find | 


# **test_lab_service_create_test_lab**
> V1CreateTestLabResponse test_lab_service_create_test_lab(test_lab)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_create_test_lab_response import V1CreateTestLabResponse
from eval_studio_client.api.models.v1_test_lab import V1TestLab
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
    api_instance = eval_studio_client.api.TestLabServiceApi(api_client)
    test_lab = eval_studio_client.api.V1TestLab() # V1TestLab | The Test Lab to create.

    try:
        api_response = api_instance.test_lab_service_create_test_lab(test_lab)
        print("The response of TestLabServiceApi->test_lab_service_create_test_lab:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestLabServiceApi->test_lab_service_create_test_lab: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_lab** | [**V1TestLab**](V1TestLab.md)| The Test Lab to create. | 

### Return type

[**V1CreateTestLabResponse**](V1CreateTestLabResponse.md)

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

# **test_lab_service_find_test_lab**
> V1FindTestLabResponse test_lab_service_find_test_lab(model=model, test_cases=test_cases, llm_models=llm_models, model_parameters=model_parameters, h2ogpte_collection=h2ogpte_collection)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_find_test_lab_response import V1FindTestLabResponse
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
    api_instance = eval_studio_client.api.TestLabServiceApi(api_client)
    model = 'model_example' # str | The Model to find Test Lab for. (optional)
    test_cases = ['test_cases_example'] # List[str] | The Test Cases to find Test Lab for. (optional)
    llm_models = ['llm_models_example'] # List[str] | The LLM models to find Test Lab for. (optional)
    model_parameters = 'model_parameters_example' # str | The parameters to find Test Lab for. (optional)
    h2ogpte_collection = 'h2ogpte_collection_example' # str | The existing collection name in H2OGPTe. (optional)

    try:
        api_response = api_instance.test_lab_service_find_test_lab(model=model, test_cases=test_cases, llm_models=llm_models, model_parameters=model_parameters, h2ogpte_collection=h2ogpte_collection)
        print("The response of TestLabServiceApi->test_lab_service_find_test_lab:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestLabServiceApi->test_lab_service_find_test_lab: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model** | **str**| The Model to find Test Lab for. | [optional] 
 **test_cases** | [**List[str]**](str.md)| The Test Cases to find Test Lab for. | [optional] 
 **llm_models** | [**List[str]**](str.md)| The LLM models to find Test Lab for. | [optional] 
 **model_parameters** | **str**| The parameters to find Test Lab for. | [optional] 
 **h2ogpte_collection** | **str**| The existing collection name in H2OGPTe. | [optional] 

### Return type

[**V1FindTestLabResponse**](V1FindTestLabResponse.md)

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

