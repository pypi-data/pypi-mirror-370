# eval_studio_client.api.TestCaseRelationshipServiceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**test_case_relationship_service_list_test_case_relationships**](TestCaseRelationshipServiceApi.md#test_case_relationship_service_list_test_case_relationships) | **GET** /v1/{parent}/testCaseRelationships | 


# **test_case_relationship_service_list_test_case_relationships**
> V1ListTestCaseRelationshipsResponse test_case_relationship_service_list_test_case_relationships(parent)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_list_test_case_relationships_response import V1ListTestCaseRelationshipsResponse
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
    api_instance = eval_studio_client.api.TestCaseRelationshipServiceApi(api_client)
    parent = 'parent_example' # str | The name of the Test whose TestCaseRelationships to retrieve.

    try:
        api_response = api_instance.test_case_relationship_service_list_test_case_relationships(parent)
        print("The response of TestCaseRelationshipServiceApi->test_case_relationship_service_list_test_case_relationships:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseRelationshipServiceApi->test_case_relationship_service_list_test_case_relationships: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **parent** | **str**| The name of the Test whose TestCaseRelationships to retrieve. | 

### Return type

[**V1ListTestCaseRelationshipsResponse**](V1ListTestCaseRelationshipsResponse.md)

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

