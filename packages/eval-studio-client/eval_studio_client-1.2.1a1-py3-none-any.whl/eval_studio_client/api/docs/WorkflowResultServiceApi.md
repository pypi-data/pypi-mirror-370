# eval_studio_client.api.WorkflowResultServiceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**workflow_result_service_get_workflow_result_corpus_patch**](WorkflowResultServiceApi.md#workflow_result_service_get_workflow_result_corpus_patch) | **GET** /v1/{name}:getResultsCorpusPatch | GetWorkflowResultCorpusPatch retrieves the corpus patch of a Workflow result. The corpus patch is a HTML document that contains questions and answers identified as problematic in HEC and RT IV workflow steps.
[**workflow_result_service_get_workflow_result_report**](WorkflowResultServiceApi.md#workflow_result_service_get_workflow_result_report) | **GET** /v1/{name}:getResultsReport | GetWorkflowResultReport retrieves the report of a Workflow result. The report is a detailed HTML document summarizing the Workflow&#39;s execution and findings.
[**workflow_result_service_get_workflow_result_summary**](WorkflowResultServiceApi.md#workflow_result_service_get_workflow_result_summary) | **GET** /v1/{name}:getResultsSummary | GetWorkflowResultSummary retrieves the 3x3x3 summary of a Workflow result. The summary includes 3 summary sentences, 3 bullets with most serious highlights, and 3 recommended actions sentences.
[**workflow_result_service_get_workflow_result_system_prompt_patch**](WorkflowResultServiceApi.md#workflow_result_service_get_workflow_result_system_prompt_patch) | **GET** /v1/{name}:getResultsSystemPromptPatch | GetWorkflowResultSystemPromptPatch retrieves the system prompt patch of a Workflow result.


# **workflow_result_service_get_workflow_result_corpus_patch**
> V1GetWorkflowResultCorpusPatchResponse workflow_result_service_get_workflow_result_corpus_patch(name)

GetWorkflowResultCorpusPatch retrieves the corpus patch of a Workflow result. The corpus patch is a HTML document that contains questions and answers identified as problematic in HEC and RT IV workflow steps.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_get_workflow_result_corpus_patch_response import V1GetWorkflowResultCorpusPatchResponse
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
    api_instance = eval_studio_client.api.WorkflowResultServiceApi(api_client)
    name = 'name_example' # str | Required. The resource name of the workflow for which to generate the corpus patch.

    try:
        # GetWorkflowResultCorpusPatch retrieves the corpus patch of a Workflow result. The corpus patch is a HTML document that contains questions and answers identified as problematic in HEC and RT IV workflow steps.
        api_response = api_instance.workflow_result_service_get_workflow_result_corpus_patch(name)
        print("The response of WorkflowResultServiceApi->workflow_result_service_get_workflow_result_corpus_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowResultServiceApi->workflow_result_service_get_workflow_result_corpus_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Required. The resource name of the workflow for which to generate the corpus patch. | 

### Return type

[**V1GetWorkflowResultCorpusPatchResponse**](V1GetWorkflowResultCorpusPatchResponse.md)

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

# **workflow_result_service_get_workflow_result_report**
> V1GetWorkflowResultReportResponse workflow_result_service_get_workflow_result_report(name, format=format)

GetWorkflowResultReport retrieves the report of a Workflow result. The report is a detailed HTML document summarizing the Workflow's execution and findings.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_get_workflow_result_report_response import V1GetWorkflowResultReportResponse
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
    api_instance = eval_studio_client.api.WorkflowResultServiceApi(api_client)
    name = 'name_example' # str | Required. The resource name of the workflow for which to retrieve the report.
    format = 'WORKFLOW_RESULT_REPORT_FORMAT_UNSPECIFIED' # str | Required. The format of the report to retrieve. (optional) (default to 'WORKFLOW_RESULT_REPORT_FORMAT_UNSPECIFIED')

    try:
        # GetWorkflowResultReport retrieves the report of a Workflow result. The report is a detailed HTML document summarizing the Workflow's execution and findings.
        api_response = api_instance.workflow_result_service_get_workflow_result_report(name, format=format)
        print("The response of WorkflowResultServiceApi->workflow_result_service_get_workflow_result_report:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowResultServiceApi->workflow_result_service_get_workflow_result_report: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Required. The resource name of the workflow for which to retrieve the report. | 
 **format** | **str**| Required. The format of the report to retrieve. | [optional] [default to &#39;WORKFLOW_RESULT_REPORT_FORMAT_UNSPECIFIED&#39;]

### Return type

[**V1GetWorkflowResultReportResponse**](V1GetWorkflowResultReportResponse.md)

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

# **workflow_result_service_get_workflow_result_summary**
> V1GetWorkflowResultSummaryResponse workflow_result_service_get_workflow_result_summary(name)

GetWorkflowResultSummary retrieves the 3x3x3 summary of a Workflow result. The summary includes 3 summary sentences, 3 bullets with most serious highlights, and 3 recommended actions sentences.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_get_workflow_result_summary_response import V1GetWorkflowResultSummaryResponse
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
    api_instance = eval_studio_client.api.WorkflowResultServiceApi(api_client)
    name = 'name_example' # str | Required. The name of the Workflow for which to retrieve the 3x3x3 summary.

    try:
        # GetWorkflowResultSummary retrieves the 3x3x3 summary of a Workflow result. The summary includes 3 summary sentences, 3 bullets with most serious highlights, and 3 recommended actions sentences.
        api_response = api_instance.workflow_result_service_get_workflow_result_summary(name)
        print("The response of WorkflowResultServiceApi->workflow_result_service_get_workflow_result_summary:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowResultServiceApi->workflow_result_service_get_workflow_result_summary: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Required. The name of the Workflow for which to retrieve the 3x3x3 summary. | 

### Return type

[**V1GetWorkflowResultSummaryResponse**](V1GetWorkflowResultSummaryResponse.md)

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

# **workflow_result_service_get_workflow_result_system_prompt_patch**
> V1GetWorkflowResultSystemPromptPatchResponse workflow_result_service_get_workflow_result_system_prompt_patch(name)

GetWorkflowResultSystemPromptPatch retrieves the system prompt patch of a Workflow result.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_get_workflow_result_system_prompt_patch_response import V1GetWorkflowResultSystemPromptPatchResponse
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
    api_instance = eval_studio_client.api.WorkflowResultServiceApi(api_client)
    name = 'name_example' # str | Required. The resource name of the workflow for which to generate the system prompt patch.

    try:
        # GetWorkflowResultSystemPromptPatch retrieves the system prompt patch of a Workflow result.
        api_response = api_instance.workflow_result_service_get_workflow_result_system_prompt_patch(name)
        print("The response of WorkflowResultServiceApi->workflow_result_service_get_workflow_result_system_prompt_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowResultServiceApi->workflow_result_service_get_workflow_result_system_prompt_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Required. The resource name of the workflow for which to generate the system prompt patch. | 

### Return type

[**V1GetWorkflowResultSystemPromptPatchResponse**](V1GetWorkflowResultSystemPromptPatchResponse.md)

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

