# eval_studio_client.api.OperationProgressServiceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**operation_progress_service_get_operation_progress_by_parent**](OperationProgressServiceApi.md#operation_progress_service_get_operation_progress_by_parent) | **GET** /v1/{parent}/progresses:getByParent | 


# **operation_progress_service_get_operation_progress_by_parent**
> V1GetOperationProgressByParentResponse operation_progress_service_get_operation_progress_by_parent(parent)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_get_operation_progress_by_parent_response import V1GetOperationProgressByParentResponse
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
    api_instance = eval_studio_client.api.OperationProgressServiceApi(api_client)
    parent = 'parent_example' # str | Required. The name of the parent Operation.

    try:
        api_response = api_instance.operation_progress_service_get_operation_progress_by_parent(parent)
        print("The response of OperationProgressServiceApi->operation_progress_service_get_operation_progress_by_parent:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OperationProgressServiceApi->operation_progress_service_get_operation_progress_by_parent: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **parent** | **str**| Required. The name of the parent Operation. | 

### Return type

[**V1GetOperationProgressByParentResponse**](V1GetOperationProgressByParentResponse.md)

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

