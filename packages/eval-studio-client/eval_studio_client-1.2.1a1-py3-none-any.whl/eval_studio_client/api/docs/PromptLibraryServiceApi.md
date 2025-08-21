# eval_studio_client.api.PromptLibraryServiceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**prompt_library_service_import_test_cases**](PromptLibraryServiceApi.md#prompt_library_service_import_test_cases) | **POST** /v1/promptLibraryItems:importTestCases | 
[**prompt_library_service_list_prompt_library_items**](PromptLibraryServiceApi.md#prompt_library_service_list_prompt_library_items) | **GET** /v1/promptLibraryItems | 


# **prompt_library_service_import_test_cases**
> V1Operation prompt_library_service_import_test_cases(body)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_import_test_cases_request import V1ImportTestCasesRequest
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
    api_instance = eval_studio_client.api.PromptLibraryServiceApi(api_client)
    body = eval_studio_client.api.V1ImportTestCasesRequest() # V1ImportTestCasesRequest | 

    try:
        api_response = api_instance.prompt_library_service_import_test_cases(body)
        print("The response of PromptLibraryServiceApi->prompt_library_service_import_test_cases:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PromptLibraryServiceApi->prompt_library_service_import_test_cases: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**V1ImportTestCasesRequest**](V1ImportTestCasesRequest.md)|  | 

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

# **prompt_library_service_list_prompt_library_items**
> V1ListPromptLibraryItemsResponse prompt_library_service_list_prompt_library_items(filter_by_categories=filter_by_categories, filter_by_purposes=filter_by_purposes, filter_by_evaluates=filter_by_evaluates, filter_by_origin=filter_by_origin, filter_by_test_case_count=filter_by_test_case_count, filter_by_test_count=filter_by_test_count, filter_by_fts=filter_by_fts)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_list_prompt_library_items_response import V1ListPromptLibraryItemsResponse
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
    api_instance = eval_studio_client.api.PromptLibraryServiceApi(api_client)
    filter_by_categories = ['filter_by_categories_example'] # List[str] | Optional. Filter by categories. (optional)
    filter_by_purposes = ['filter_by_purposes_example'] # List[str] | Optional. Filter by purposes. (optional)
    filter_by_evaluates = ['filter_by_evaluates_example'] # List[str] | Optional. Filter by evaluates. (optional)
    filter_by_origin = 'filter_by_origin_example' # str | Optional. Filter by origin. (optional)
    filter_by_test_case_count = 56 # int | Optional. Filter by test case count. (optional)
    filter_by_test_count = 56 # int | Optional. Filter by test count. (optional)
    filter_by_fts = 'filter_by_fts_example' # str | Optional. Filter by FTS. (optional)

    try:
        api_response = api_instance.prompt_library_service_list_prompt_library_items(filter_by_categories=filter_by_categories, filter_by_purposes=filter_by_purposes, filter_by_evaluates=filter_by_evaluates, filter_by_origin=filter_by_origin, filter_by_test_case_count=filter_by_test_case_count, filter_by_test_count=filter_by_test_count, filter_by_fts=filter_by_fts)
        print("The response of PromptLibraryServiceApi->prompt_library_service_list_prompt_library_items:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PromptLibraryServiceApi->prompt_library_service_list_prompt_library_items: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filter_by_categories** | [**List[str]**](str.md)| Optional. Filter by categories. | [optional] 
 **filter_by_purposes** | [**List[str]**](str.md)| Optional. Filter by purposes. | [optional] 
 **filter_by_evaluates** | [**List[str]**](str.md)| Optional. Filter by evaluates. | [optional] 
 **filter_by_origin** | **str**| Optional. Filter by origin. | [optional] 
 **filter_by_test_case_count** | **int**| Optional. Filter by test case count. | [optional] 
 **filter_by_test_count** | **int**| Optional. Filter by test count. | [optional] 
 **filter_by_fts** | **str**| Optional. Filter by FTS. | [optional] 

### Return type

[**V1ListPromptLibraryItemsResponse**](V1ListPromptLibraryItemsResponse.md)

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

