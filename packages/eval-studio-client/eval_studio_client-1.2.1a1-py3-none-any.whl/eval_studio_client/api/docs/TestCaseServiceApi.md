# eval_studio_client.api.TestCaseServiceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**test_case_service_batch_delete_test_cases**](TestCaseServiceApi.md#test_case_service_batch_delete_test_cases) | **POST** /v1/{parent}/testCases:batchDelete | 
[**test_case_service_create_test_case**](TestCaseServiceApi.md#test_case_service_create_test_case) | **POST** /v1/{parent}/testCases | 
[**test_case_service_delete_test_case**](TestCaseServiceApi.md#test_case_service_delete_test_case) | **DELETE** /v1/{name_5} | 
[**test_case_service_find_all_test_cases_by_id**](TestCaseServiceApi.md#test_case_service_find_all_test_cases_by_id) | **GET** /v1/tests/-/testCases:findAllTestCasesByID | 
[**test_case_service_get_test_case**](TestCaseServiceApi.md#test_case_service_get_test_case) | **GET** /v1/{name_8} | 
[**test_case_service_list_test_cases**](TestCaseServiceApi.md#test_case_service_list_test_cases) | **GET** /v1/{parent}/testCases | 
[**test_case_service_update_test_case**](TestCaseServiceApi.md#test_case_service_update_test_case) | **PATCH** /v1/{testCase.name} | 


# **test_case_service_batch_delete_test_cases**
> V1BatchDeleteTestCasesResponse test_case_service_batch_delete_test_cases(parent, body)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.test_case_service_batch_delete_test_cases_request import TestCaseServiceBatchDeleteTestCasesRequest
from eval_studio_client.api.models.v1_batch_delete_test_cases_response import V1BatchDeleteTestCasesResponse
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
    api_instance = eval_studio_client.api.TestCaseServiceApi(api_client)
    parent = 'parent_example' # str | The parent Test whose TestCases will be deleted.  Format: tests/<UUID>  If this is set, the parent of all of the TestCases specified in `names` must match this field.
    body = eval_studio_client.api.TestCaseServiceBatchDeleteTestCasesRequest() # TestCaseServiceBatchDeleteTestCasesRequest | 

    try:
        api_response = api_instance.test_case_service_batch_delete_test_cases(parent, body)
        print("The response of TestCaseServiceApi->test_case_service_batch_delete_test_cases:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseServiceApi->test_case_service_batch_delete_test_cases: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **parent** | **str**| The parent Test whose TestCases will be deleted.  Format: tests/&lt;UUID&gt;  If this is set, the parent of all of the TestCases specified in &#x60;names&#x60; must match this field. | 
 **body** | [**TestCaseServiceBatchDeleteTestCasesRequest**](TestCaseServiceBatchDeleteTestCasesRequest.md)|  | 

### Return type

[**V1BatchDeleteTestCasesResponse**](V1BatchDeleteTestCasesResponse.md)

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

# **test_case_service_create_test_case**
> V1CreateTestCaseResponse test_case_service_create_test_case(parent, test_case)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_create_test_case_response import V1CreateTestCaseResponse
from eval_studio_client.api.models.v1_test_case import V1TestCase
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
    api_instance = eval_studio_client.api.TestCaseServiceApi(api_client)
    parent = 'parent_example' # str | The parent Test where this TestCase will be created. Format: tests/<UUID>
    test_case = eval_studio_client.api.V1TestCase() # V1TestCase | The TestCase to create.

    try:
        api_response = api_instance.test_case_service_create_test_case(parent, test_case)
        print("The response of TestCaseServiceApi->test_case_service_create_test_case:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseServiceApi->test_case_service_create_test_case: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **parent** | **str**| The parent Test where this TestCase will be created. Format: tests/&lt;UUID&gt; | 
 **test_case** | [**V1TestCase**](V1TestCase.md)| The TestCase to create. | 

### Return type

[**V1CreateTestCaseResponse**](V1CreateTestCaseResponse.md)

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

# **test_case_service_delete_test_case**
> V1DeleteTestCaseResponse test_case_service_delete_test_case(name_5)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_delete_test_case_response import V1DeleteTestCaseResponse
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
    api_instance = eval_studio_client.api.TestCaseServiceApi(api_client)
    name_5 = 'name_5_example' # str | The name of the TestCase to delete. Format: tests/<UUID>/testCases/<UUID>

    try:
        api_response = api_instance.test_case_service_delete_test_case(name_5)
        print("The response of TestCaseServiceApi->test_case_service_delete_test_case:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseServiceApi->test_case_service_delete_test_case: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name_5** | **str**| The name of the TestCase to delete. Format: tests/&lt;UUID&gt;/testCases/&lt;UUID&gt; | 

### Return type

[**V1DeleteTestCaseResponse**](V1DeleteTestCaseResponse.md)

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

# **test_case_service_find_all_test_cases_by_id**
> V1FindAllTestCasesByIDResponse test_case_service_find_all_test_cases_by_id(ids=ids)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_find_all_test_cases_by_id_response import V1FindAllTestCasesByIDResponse
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
    api_instance = eval_studio_client.api.TestCaseServiceApi(api_client)
    ids = ['ids_example'] # List[str] | The list of TestCase IDs to retrieve. (optional)

    try:
        api_response = api_instance.test_case_service_find_all_test_cases_by_id(ids=ids)
        print("The response of TestCaseServiceApi->test_case_service_find_all_test_cases_by_id:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseServiceApi->test_case_service_find_all_test_cases_by_id: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **ids** | [**List[str]**](str.md)| The list of TestCase IDs to retrieve. | [optional] 

### Return type

[**V1FindAllTestCasesByIDResponse**](V1FindAllTestCasesByIDResponse.md)

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

# **test_case_service_get_test_case**
> V1GetTestCaseResponse test_case_service_get_test_case(name_8)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_get_test_case_response import V1GetTestCaseResponse
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
    api_instance = eval_studio_client.api.TestCaseServiceApi(api_client)
    name_8 = 'name_8_example' # str | The name of the TestCase to retrieve. Format: tests/<UUID>/testCases/<UUID>

    try:
        api_response = api_instance.test_case_service_get_test_case(name_8)
        print("The response of TestCaseServiceApi->test_case_service_get_test_case:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseServiceApi->test_case_service_get_test_case: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name_8** | **str**| The name of the TestCase to retrieve. Format: tests/&lt;UUID&gt;/testCases/&lt;UUID&gt; | 

### Return type

[**V1GetTestCaseResponse**](V1GetTestCaseResponse.md)

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

# **test_case_service_list_test_cases**
> V1ListTestCasesResponse test_case_service_list_test_cases(parent)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_list_test_cases_response import V1ListTestCasesResponse
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
    api_instance = eval_studio_client.api.TestCaseServiceApi(api_client)
    parent = 'parent_example' # str | The parent Test whose TestCases will be listed. Format: tests/<UUID>

    try:
        api_response = api_instance.test_case_service_list_test_cases(parent)
        print("The response of TestCaseServiceApi->test_case_service_list_test_cases:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseServiceApi->test_case_service_list_test_cases: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **parent** | **str**| The parent Test whose TestCases will be listed. Format: tests/&lt;UUID&gt; | 

### Return type

[**V1ListTestCasesResponse**](V1ListTestCasesResponse.md)

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

# **test_case_service_update_test_case**
> V1UpdateTestCaseResponse test_case_service_update_test_case(test_case_name, test_case)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.required_the_test_case_to_update import RequiredTheTestCaseToUpdate
from eval_studio_client.api.models.v1_update_test_case_response import V1UpdateTestCaseResponse
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
    api_instance = eval_studio_client.api.TestCaseServiceApi(api_client)
    test_case_name = 'test_case_name_example' # str | Output only. Name of the prompt resource. e.g.: \"tests/<UUID>/testCases/<UUID>\"
    test_case = eval_studio_client.api.RequiredTheTestCaseToUpdate() # RequiredTheTestCaseToUpdate | Required. The TestCase to update.

    try:
        api_response = api_instance.test_case_service_update_test_case(test_case_name, test_case)
        print("The response of TestCaseServiceApi->test_case_service_update_test_case:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TestCaseServiceApi->test_case_service_update_test_case: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_case_name** | **str**| Output only. Name of the prompt resource. e.g.: \&quot;tests/&lt;UUID&gt;/testCases/&lt;UUID&gt;\&quot; | 
 **test_case** | [**RequiredTheTestCaseToUpdate**](RequiredTheTestCaseToUpdate.md)| Required. The TestCase to update. | 

### Return type

[**V1UpdateTestCaseResponse**](V1UpdateTestCaseResponse.md)

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

