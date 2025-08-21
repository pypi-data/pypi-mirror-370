# eval_studio_client.api.EvaluatorServiceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**evaluator_service_batch_delete_evaluators**](EvaluatorServiceApi.md#evaluator_service_batch_delete_evaluators) | **POST** /v1/evaluators:batchDelete | 
[**evaluator_service_create_evaluator**](EvaluatorServiceApi.md#evaluator_service_create_evaluator) | **POST** /v1/evaluators | 
[**evaluator_service_delete_evaluator**](EvaluatorServiceApi.md#evaluator_service_delete_evaluator) | **DELETE** /v1/{name_2} | 
[**evaluator_service_get_evaluator**](EvaluatorServiceApi.md#evaluator_service_get_evaluator) | **GET** /v1/{name_2} | 
[**evaluator_service_list_evaluators**](EvaluatorServiceApi.md#evaluator_service_list_evaluators) | **GET** /v1/evaluators | 


# **evaluator_service_batch_delete_evaluators**
> V1BatchDeleteEvaluatorsResponse evaluator_service_batch_delete_evaluators(body)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_batch_delete_evaluators_request import V1BatchDeleteEvaluatorsRequest
from eval_studio_client.api.models.v1_batch_delete_evaluators_response import V1BatchDeleteEvaluatorsResponse
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
    api_instance = eval_studio_client.api.EvaluatorServiceApi(api_client)
    body = eval_studio_client.api.V1BatchDeleteEvaluatorsRequest() # V1BatchDeleteEvaluatorsRequest | 

    try:
        api_response = api_instance.evaluator_service_batch_delete_evaluators(body)
        print("The response of EvaluatorServiceApi->evaluator_service_batch_delete_evaluators:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EvaluatorServiceApi->evaluator_service_batch_delete_evaluators: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**V1BatchDeleteEvaluatorsRequest**](V1BatchDeleteEvaluatorsRequest.md)|  | 

### Return type

[**V1BatchDeleteEvaluatorsResponse**](V1BatchDeleteEvaluatorsResponse.md)

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

# **evaluator_service_create_evaluator**
> V1CreateEvaluatorResponse evaluator_service_create_evaluator(evaluator)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_create_evaluator_response import V1CreateEvaluatorResponse
from eval_studio_client.api.models.v1_evaluator import V1Evaluator
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
    api_instance = eval_studio_client.api.EvaluatorServiceApi(api_client)
    evaluator = eval_studio_client.api.V1Evaluator() # V1Evaluator | Required. The Evaluator to create.

    try:
        api_response = api_instance.evaluator_service_create_evaluator(evaluator)
        print("The response of EvaluatorServiceApi->evaluator_service_create_evaluator:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EvaluatorServiceApi->evaluator_service_create_evaluator: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **evaluator** | [**V1Evaluator**](V1Evaluator.md)| Required. The Evaluator to create. | 

### Return type

[**V1CreateEvaluatorResponse**](V1CreateEvaluatorResponse.md)

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

# **evaluator_service_delete_evaluator**
> V1DeleteEvaluatorResponse evaluator_service_delete_evaluator(name_2)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_delete_evaluator_response import V1DeleteEvaluatorResponse
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
    api_instance = eval_studio_client.api.EvaluatorServiceApi(api_client)
    name_2 = 'name_2_example' # str | Required. The name of the Evaluator to delete.

    try:
        api_response = api_instance.evaluator_service_delete_evaluator(name_2)
        print("The response of EvaluatorServiceApi->evaluator_service_delete_evaluator:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EvaluatorServiceApi->evaluator_service_delete_evaluator: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name_2** | **str**| Required. The name of the Evaluator to delete. | 

### Return type

[**V1DeleteEvaluatorResponse**](V1DeleteEvaluatorResponse.md)

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

# **evaluator_service_get_evaluator**
> V1GetEvaluatorResponse evaluator_service_get_evaluator(name_2)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_get_evaluator_response import V1GetEvaluatorResponse
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
    api_instance = eval_studio_client.api.EvaluatorServiceApi(api_client)
    name_2 = 'name_2_example' # str | Required. The name of the Evaluator to retrieve.

    try:
        api_response = api_instance.evaluator_service_get_evaluator(name_2)
        print("The response of EvaluatorServiceApi->evaluator_service_get_evaluator:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EvaluatorServiceApi->evaluator_service_get_evaluator: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name_2** | **str**| Required. The name of the Evaluator to retrieve. | 

### Return type

[**V1GetEvaluatorResponse**](V1GetEvaluatorResponse.md)

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

# **evaluator_service_list_evaluators**
> V1ListEvaluatorsResponse evaluator_service_list_evaluators(view=view)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_list_evaluators_response import V1ListEvaluatorsResponse
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
    api_instance = eval_studio_client.api.EvaluatorServiceApi(api_client)
    view = 'EVALUATOR_VIEW_UNSPECIFIED' # str | Optional. View specifies the amount of information included in the Evaluator's description. Brief view includes only short descriptions, which can significantly decrease the amount of data transferred.   - EVALUATOR_VIEW_UNSPECIFIED: The default / unset value. The API will default to the EVALUATOR_VIEW_BRIEF.  - EVALUATOR_VIEW_BRIEF: Brief view of the Evaluator, which doesn't include the long description, only the brief one.  - EVALUATOR_VIEW_FULL: Full view of the evaluator, including brief and full description. (optional) (default to 'EVALUATOR_VIEW_UNSPECIFIED')

    try:
        api_response = api_instance.evaluator_service_list_evaluators(view=view)
        print("The response of EvaluatorServiceApi->evaluator_service_list_evaluators:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EvaluatorServiceApi->evaluator_service_list_evaluators: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **view** | **str**| Optional. View specifies the amount of information included in the Evaluator&#39;s description. Brief view includes only short descriptions, which can significantly decrease the amount of data transferred.   - EVALUATOR_VIEW_UNSPECIFIED: The default / unset value. The API will default to the EVALUATOR_VIEW_BRIEF.  - EVALUATOR_VIEW_BRIEF: Brief view of the Evaluator, which doesn&#39;t include the long description, only the brief one.  - EVALUATOR_VIEW_FULL: Full view of the evaluator, including brief and full description. | [optional] [default to &#39;EVALUATOR_VIEW_UNSPECIFIED&#39;]

### Return type

[**V1ListEvaluatorsResponse**](V1ListEvaluatorsResponse.md)

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

