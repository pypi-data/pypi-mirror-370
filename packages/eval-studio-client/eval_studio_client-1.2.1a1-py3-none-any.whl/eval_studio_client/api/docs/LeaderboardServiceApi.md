# eval_studio_client.api.LeaderboardServiceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**leaderboard_service_batch_create_leaderboards**](LeaderboardServiceApi.md#leaderboard_service_batch_create_leaderboards) | **POST** /v1/leaderboards:batchCreate | 
[**leaderboard_service_batch_delete_leaderboards**](LeaderboardServiceApi.md#leaderboard_service_batch_delete_leaderboards) | **POST** /v1/leaderboards:batchDelete | 
[**leaderboard_service_batch_get_leaderboards**](LeaderboardServiceApi.md#leaderboard_service_batch_get_leaderboards) | **GET** /v1/leaderboards:batchGet | 
[**leaderboard_service_batch_import_leaderboard**](LeaderboardServiceApi.md#leaderboard_service_batch_import_leaderboard) | **POST** /v1/leaderboards:batchImport | 
[**leaderboard_service_create_leaderboard**](LeaderboardServiceApi.md#leaderboard_service_create_leaderboard) | **POST** /v1/leaderboards | 
[**leaderboard_service_create_leaderboard_without_cache**](LeaderboardServiceApi.md#leaderboard_service_create_leaderboard_without_cache) | **POST** /v1/leaderboards:withoutCache | 
[**leaderboard_service_delete_leaderboard**](LeaderboardServiceApi.md#leaderboard_service_delete_leaderboard) | **DELETE** /v1/{name_3} | 
[**leaderboard_service_get_leaderboard**](LeaderboardServiceApi.md#leaderboard_service_get_leaderboard) | **GET** /v1/{name_4} | 
[**leaderboard_service_import_leaderboard**](LeaderboardServiceApi.md#leaderboard_service_import_leaderboard) | **POST** /v1/leaderboards:import | 
[**leaderboard_service_list_leaderboards**](LeaderboardServiceApi.md#leaderboard_service_list_leaderboards) | **GET** /v1/leaderboards | 
[**leaderboard_service_list_most_recent_leaderboards**](LeaderboardServiceApi.md#leaderboard_service_list_most_recent_leaderboards) | **GET** /v1/leaderboards:mostRecent | 
[**leaderboard_service_update_leaderboard**](LeaderboardServiceApi.md#leaderboard_service_update_leaderboard) | **PATCH** /v1/{leaderboard.name} | 


# **leaderboard_service_batch_create_leaderboards**
> V1BatchCreateLeaderboardsResponse leaderboard_service_batch_create_leaderboards(body)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_batch_create_leaderboards_request import V1BatchCreateLeaderboardsRequest
from eval_studio_client.api.models.v1_batch_create_leaderboards_response import V1BatchCreateLeaderboardsResponse
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
    api_instance = eval_studio_client.api.LeaderboardServiceApi(api_client)
    body = eval_studio_client.api.V1BatchCreateLeaderboardsRequest() # V1BatchCreateLeaderboardsRequest | 

    try:
        api_response = api_instance.leaderboard_service_batch_create_leaderboards(body)
        print("The response of LeaderboardServiceApi->leaderboard_service_batch_create_leaderboards:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LeaderboardServiceApi->leaderboard_service_batch_create_leaderboards: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**V1BatchCreateLeaderboardsRequest**](V1BatchCreateLeaderboardsRequest.md)|  | 

### Return type

[**V1BatchCreateLeaderboardsResponse**](V1BatchCreateLeaderboardsResponse.md)

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

# **leaderboard_service_batch_delete_leaderboards**
> V1BatchDeleteLeaderboardsResponse leaderboard_service_batch_delete_leaderboards(body)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_batch_delete_leaderboards_request import V1BatchDeleteLeaderboardsRequest
from eval_studio_client.api.models.v1_batch_delete_leaderboards_response import V1BatchDeleteLeaderboardsResponse
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
    api_instance = eval_studio_client.api.LeaderboardServiceApi(api_client)
    body = eval_studio_client.api.V1BatchDeleteLeaderboardsRequest() # V1BatchDeleteLeaderboardsRequest | 

    try:
        api_response = api_instance.leaderboard_service_batch_delete_leaderboards(body)
        print("The response of LeaderboardServiceApi->leaderboard_service_batch_delete_leaderboards:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LeaderboardServiceApi->leaderboard_service_batch_delete_leaderboards: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**V1BatchDeleteLeaderboardsRequest**](V1BatchDeleteLeaderboardsRequest.md)|  | 

### Return type

[**V1BatchDeleteLeaderboardsResponse**](V1BatchDeleteLeaderboardsResponse.md)

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

# **leaderboard_service_batch_get_leaderboards**
> V1BatchGetLeaderboardsResponse leaderboard_service_batch_get_leaderboards(names=names, view=view)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_batch_get_leaderboards_response import V1BatchGetLeaderboardsResponse
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
    api_instance = eval_studio_client.api.LeaderboardServiceApi(api_client)
    names = ['names_example'] # List[str] | Required. The names of the Leaderboards to retrieve. A maximum of 1000 can be specified. (optional)
    view = 'LEADERBOARD_VIEW_UNSPECIFIED' # str | Optional. View specifying which fields should be returned in the response. Defaults to LEADERBOARD_VIEW_BASIC.   - LEADERBOARD_VIEW_UNSPECIFIED: The default / unset value. The API will default to the LEADERBOARD_VIEW_BASIC.  - LEADERBOARD_VIEW_BASIC: Basic view of the Leaderboard. The following fields are omitted in the response:  - result - leaderboard_table - leaderboard_summary  - LEADERBOARD_VIEW_FULL: Full view of the Leaderboard. No fields are omitted.  - LEADERBOARD_VIEW_BASIC_WITH_TABLE: View of the Leaderboard that is the same as LEADERBOARD_VIEW_BASIC but it includes the leaderboard_table field. (optional) (default to 'LEADERBOARD_VIEW_UNSPECIFIED')

    try:
        api_response = api_instance.leaderboard_service_batch_get_leaderboards(names=names, view=view)
        print("The response of LeaderboardServiceApi->leaderboard_service_batch_get_leaderboards:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LeaderboardServiceApi->leaderboard_service_batch_get_leaderboards: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **names** | [**List[str]**](str.md)| Required. The names of the Leaderboards to retrieve. A maximum of 1000 can be specified. | [optional] 
 **view** | **str**| Optional. View specifying which fields should be returned in the response. Defaults to LEADERBOARD_VIEW_BASIC.   - LEADERBOARD_VIEW_UNSPECIFIED: The default / unset value. The API will default to the LEADERBOARD_VIEW_BASIC.  - LEADERBOARD_VIEW_BASIC: Basic view of the Leaderboard. The following fields are omitted in the response:  - result - leaderboard_table - leaderboard_summary  - LEADERBOARD_VIEW_FULL: Full view of the Leaderboard. No fields are omitted.  - LEADERBOARD_VIEW_BASIC_WITH_TABLE: View of the Leaderboard that is the same as LEADERBOARD_VIEW_BASIC but it includes the leaderboard_table field. | [optional] [default to &#39;LEADERBOARD_VIEW_UNSPECIFIED&#39;]

### Return type

[**V1BatchGetLeaderboardsResponse**](V1BatchGetLeaderboardsResponse.md)

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

# **leaderboard_service_batch_import_leaderboard**
> V1BatchImportLeaderboardResponse leaderboard_service_batch_import_leaderboard(body)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_batch_import_leaderboard_request import V1BatchImportLeaderboardRequest
from eval_studio_client.api.models.v1_batch_import_leaderboard_response import V1BatchImportLeaderboardResponse
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
    api_instance = eval_studio_client.api.LeaderboardServiceApi(api_client)
    body = eval_studio_client.api.V1BatchImportLeaderboardRequest() # V1BatchImportLeaderboardRequest | 

    try:
        api_response = api_instance.leaderboard_service_batch_import_leaderboard(body)
        print("The response of LeaderboardServiceApi->leaderboard_service_batch_import_leaderboard:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LeaderboardServiceApi->leaderboard_service_batch_import_leaderboard: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**V1BatchImportLeaderboardRequest**](V1BatchImportLeaderboardRequest.md)|  | 

### Return type

[**V1BatchImportLeaderboardResponse**](V1BatchImportLeaderboardResponse.md)

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

# **leaderboard_service_create_leaderboard**
> V1CreateLeaderboardResponse leaderboard_service_create_leaderboard(leaderboard)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_create_leaderboard_response import V1CreateLeaderboardResponse
from eval_studio_client.api.models.v1_leaderboard import V1Leaderboard
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
    api_instance = eval_studio_client.api.LeaderboardServiceApi(api_client)
    leaderboard = eval_studio_client.api.V1Leaderboard() # V1Leaderboard | Required. The Leaderboard to create.

    try:
        api_response = api_instance.leaderboard_service_create_leaderboard(leaderboard)
        print("The response of LeaderboardServiceApi->leaderboard_service_create_leaderboard:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LeaderboardServiceApi->leaderboard_service_create_leaderboard: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **leaderboard** | [**V1Leaderboard**](V1Leaderboard.md)| Required. The Leaderboard to create. | 

### Return type

[**V1CreateLeaderboardResponse**](V1CreateLeaderboardResponse.md)

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

# **leaderboard_service_create_leaderboard_without_cache**
> V1CreateLeaderboardWithoutCacheResponse leaderboard_service_create_leaderboard_without_cache(leaderboard)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_create_leaderboard_without_cache_response import V1CreateLeaderboardWithoutCacheResponse
from eval_studio_client.api.models.v1_leaderboard import V1Leaderboard
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
    api_instance = eval_studio_client.api.LeaderboardServiceApi(api_client)
    leaderboard = eval_studio_client.api.V1Leaderboard() # V1Leaderboard | Required. The Leaderboard to create.

    try:
        api_response = api_instance.leaderboard_service_create_leaderboard_without_cache(leaderboard)
        print("The response of LeaderboardServiceApi->leaderboard_service_create_leaderboard_without_cache:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LeaderboardServiceApi->leaderboard_service_create_leaderboard_without_cache: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **leaderboard** | [**V1Leaderboard**](V1Leaderboard.md)| Required. The Leaderboard to create. | 

### Return type

[**V1CreateLeaderboardWithoutCacheResponse**](V1CreateLeaderboardWithoutCacheResponse.md)

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

# **leaderboard_service_delete_leaderboard**
> V1DeleteLeaderboardResponse leaderboard_service_delete_leaderboard(name_3)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_delete_leaderboard_response import V1DeleteLeaderboardResponse
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
    api_instance = eval_studio_client.api.LeaderboardServiceApi(api_client)
    name_3 = 'name_3_example' # str | Required. The name of the Leaderboard to delete.

    try:
        api_response = api_instance.leaderboard_service_delete_leaderboard(name_3)
        print("The response of LeaderboardServiceApi->leaderboard_service_delete_leaderboard:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LeaderboardServiceApi->leaderboard_service_delete_leaderboard: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name_3** | **str**| Required. The name of the Leaderboard to delete. | 

### Return type

[**V1DeleteLeaderboardResponse**](V1DeleteLeaderboardResponse.md)

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

# **leaderboard_service_get_leaderboard**
> V1GetLeaderboardResponse leaderboard_service_get_leaderboard(name_4)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_get_leaderboard_response import V1GetLeaderboardResponse
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
    api_instance = eval_studio_client.api.LeaderboardServiceApi(api_client)
    name_4 = 'name_4_example' # str | Required. The name of the Leaderboard to retrieve.

    try:
        api_response = api_instance.leaderboard_service_get_leaderboard(name_4)
        print("The response of LeaderboardServiceApi->leaderboard_service_get_leaderboard:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LeaderboardServiceApi->leaderboard_service_get_leaderboard: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name_4** | **str**| Required. The name of the Leaderboard to retrieve. | 

### Return type

[**V1GetLeaderboardResponse**](V1GetLeaderboardResponse.md)

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

# **leaderboard_service_import_leaderboard**
> V1ImportLeaderboardResponse leaderboard_service_import_leaderboard(body)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_import_leaderboard_request import V1ImportLeaderboardRequest
from eval_studio_client.api.models.v1_import_leaderboard_response import V1ImportLeaderboardResponse
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
    api_instance = eval_studio_client.api.LeaderboardServiceApi(api_client)
    body = eval_studio_client.api.V1ImportLeaderboardRequest() # V1ImportLeaderboardRequest | 

    try:
        api_response = api_instance.leaderboard_service_import_leaderboard(body)
        print("The response of LeaderboardServiceApi->leaderboard_service_import_leaderboard:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LeaderboardServiceApi->leaderboard_service_import_leaderboard: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**V1ImportLeaderboardRequest**](V1ImportLeaderboardRequest.md)|  | 

### Return type

[**V1ImportLeaderboardResponse**](V1ImportLeaderboardResponse.md)

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

# **leaderboard_service_list_leaderboards**
> V1ListLeaderboardsResponse leaderboard_service_list_leaderboards(page_size=page_size, page_token=page_token, filter=filter, order_by=order_by, view=view)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_list_leaderboards_response import V1ListLeaderboardsResponse
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
    api_instance = eval_studio_client.api.LeaderboardServiceApi(api_client)
    page_size = 56 # int | The maximum number of Leaderboards to return. The service may return fewer than this value. If unspecified, at most 20 Leaderboards will be returned. The maximum value is 50; values above 50 will be coerced to 50. (optional)
    page_token = 'page_token_example' # str | A page token, received from a previous `ListLeaderboards` call. Provide this to retrieve the subsequent page.  When paginating, all other parameters provided to `ListLeaderboards` must match the call that provided the page token. (optional)
    filter = 'filter_example' # str | Optional. If specified, only leaderboards matching the filter will be returned. Attempts to implement AIP-160 (https://aip.dev/160), although not all fields, operators and features are supported.  Supported fields: - model   - only '=' operator is supported, e.g. \"model = \\\"models/<UUID>\\\"\" (optional)
    order_by = 'order_by_example' # str | If specified, the returned leaderboards will be ordered by the specified field. Attempts to implement AIP-130 (https://google.aip.dev/132#ordering), although not all features are supported yet.  Supported fields: - create_time - update_time (optional)
    view = 'LEADERBOARD_VIEW_UNSPECIFIED' # str | Optional. View specifying which fields should be returned in the response. Defaults to LEADERBOARD_VIEW_BASIC.   - LEADERBOARD_VIEW_UNSPECIFIED: The default / unset value. The API will default to the LEADERBOARD_VIEW_BASIC.  - LEADERBOARD_VIEW_BASIC: Basic view of the Leaderboard. The following fields are omitted in the response:  - result - leaderboard_table - leaderboard_summary  - LEADERBOARD_VIEW_FULL: Full view of the Leaderboard. No fields are omitted.  - LEADERBOARD_VIEW_BASIC_WITH_TABLE: View of the Leaderboard that is the same as LEADERBOARD_VIEW_BASIC but it includes the leaderboard_table field. (optional) (default to 'LEADERBOARD_VIEW_UNSPECIFIED')

    try:
        api_response = api_instance.leaderboard_service_list_leaderboards(page_size=page_size, page_token=page_token, filter=filter, order_by=order_by, view=view)
        print("The response of LeaderboardServiceApi->leaderboard_service_list_leaderboards:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LeaderboardServiceApi->leaderboard_service_list_leaderboards: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page_size** | **int**| The maximum number of Leaderboards to return. The service may return fewer than this value. If unspecified, at most 20 Leaderboards will be returned. The maximum value is 50; values above 50 will be coerced to 50. | [optional] 
 **page_token** | **str**| A page token, received from a previous &#x60;ListLeaderboards&#x60; call. Provide this to retrieve the subsequent page.  When paginating, all other parameters provided to &#x60;ListLeaderboards&#x60; must match the call that provided the page token. | [optional] 
 **filter** | **str**| Optional. If specified, only leaderboards matching the filter will be returned. Attempts to implement AIP-160 (https://aip.dev/160), although not all fields, operators and features are supported.  Supported fields: - model   - only &#39;&#x3D;&#39; operator is supported, e.g. \&quot;model &#x3D; \\\&quot;models/&lt;UUID&gt;\\\&quot;\&quot; | [optional] 
 **order_by** | **str**| If specified, the returned leaderboards will be ordered by the specified field. Attempts to implement AIP-130 (https://google.aip.dev/132#ordering), although not all features are supported yet.  Supported fields: - create_time - update_time | [optional] 
 **view** | **str**| Optional. View specifying which fields should be returned in the response. Defaults to LEADERBOARD_VIEW_BASIC.   - LEADERBOARD_VIEW_UNSPECIFIED: The default / unset value. The API will default to the LEADERBOARD_VIEW_BASIC.  - LEADERBOARD_VIEW_BASIC: Basic view of the Leaderboard. The following fields are omitted in the response:  - result - leaderboard_table - leaderboard_summary  - LEADERBOARD_VIEW_FULL: Full view of the Leaderboard. No fields are omitted.  - LEADERBOARD_VIEW_BASIC_WITH_TABLE: View of the Leaderboard that is the same as LEADERBOARD_VIEW_BASIC but it includes the leaderboard_table field. | [optional] [default to &#39;LEADERBOARD_VIEW_UNSPECIFIED&#39;]

### Return type

[**V1ListLeaderboardsResponse**](V1ListLeaderboardsResponse.md)

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

# **leaderboard_service_list_most_recent_leaderboards**
> V1ListMostRecentLeaderboardsResponse leaderboard_service_list_most_recent_leaderboards(limit=limit, filter=filter, view=view)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_list_most_recent_leaderboards_response import V1ListMostRecentLeaderboardsResponse
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
    api_instance = eval_studio_client.api.LeaderboardServiceApi(api_client)
    limit = 56 # int | Optional. The max number of the most recent Leaderboards to retrieve. Use -1 to retrieve all. Defaults to 3. (optional)
    filter = 'filter_example' # str | Optional. If specified, only leaderboards matching the filter will be returned. Attempts to implement AIP-160 (https://aip.dev/160), although not all fields, operators and features are supported.  Supported fields: - model   - only '=' operator is supported, e.g. \"model = \\\"models/<UUID>\\\"\" (optional)
    view = 'LEADERBOARD_VIEW_UNSPECIFIED' # str | Optional. View specifying which fields should be returned in the response. Defaults to LEADERBOARD_VIEW_BASIC.   - LEADERBOARD_VIEW_UNSPECIFIED: The default / unset value. The API will default to the LEADERBOARD_VIEW_BASIC.  - LEADERBOARD_VIEW_BASIC: Basic view of the Leaderboard. The following fields are omitted in the response:  - result - leaderboard_table - leaderboard_summary  - LEADERBOARD_VIEW_FULL: Full view of the Leaderboard. No fields are omitted.  - LEADERBOARD_VIEW_BASIC_WITH_TABLE: View of the Leaderboard that is the same as LEADERBOARD_VIEW_BASIC but it includes the leaderboard_table field. (optional) (default to 'LEADERBOARD_VIEW_UNSPECIFIED')

    try:
        api_response = api_instance.leaderboard_service_list_most_recent_leaderboards(limit=limit, filter=filter, view=view)
        print("The response of LeaderboardServiceApi->leaderboard_service_list_most_recent_leaderboards:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LeaderboardServiceApi->leaderboard_service_list_most_recent_leaderboards: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| Optional. The max number of the most recent Leaderboards to retrieve. Use -1 to retrieve all. Defaults to 3. | [optional] 
 **filter** | **str**| Optional. If specified, only leaderboards matching the filter will be returned. Attempts to implement AIP-160 (https://aip.dev/160), although not all fields, operators and features are supported.  Supported fields: - model   - only &#39;&#x3D;&#39; operator is supported, e.g. \&quot;model &#x3D; \\\&quot;models/&lt;UUID&gt;\\\&quot;\&quot; | [optional] 
 **view** | **str**| Optional. View specifying which fields should be returned in the response. Defaults to LEADERBOARD_VIEW_BASIC.   - LEADERBOARD_VIEW_UNSPECIFIED: The default / unset value. The API will default to the LEADERBOARD_VIEW_BASIC.  - LEADERBOARD_VIEW_BASIC: Basic view of the Leaderboard. The following fields are omitted in the response:  - result - leaderboard_table - leaderboard_summary  - LEADERBOARD_VIEW_FULL: Full view of the Leaderboard. No fields are omitted.  - LEADERBOARD_VIEW_BASIC_WITH_TABLE: View of the Leaderboard that is the same as LEADERBOARD_VIEW_BASIC but it includes the leaderboard_table field. | [optional] [default to &#39;LEADERBOARD_VIEW_UNSPECIFIED&#39;]

### Return type

[**V1ListMostRecentLeaderboardsResponse**](V1ListMostRecentLeaderboardsResponse.md)

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

# **leaderboard_service_update_leaderboard**
> V1UpdateLeaderboardResponse leaderboard_service_update_leaderboard(leaderboard_name, leaderboard)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.required_the_leaderboard_to_update import RequiredTheLeaderboardToUpdate
from eval_studio_client.api.models.v1_update_leaderboard_response import V1UpdateLeaderboardResponse
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
    api_instance = eval_studio_client.api.LeaderboardServiceApi(api_client)
    leaderboard_name = 'leaderboard_name_example' # str | Output only. Name of the Leaderboard resource. e.g.: \"leaderboards/<UUID>\"
    leaderboard = eval_studio_client.api.RequiredTheLeaderboardToUpdate() # RequiredTheLeaderboardToUpdate | Required. The Leaderboard to update.  The Leaderboard's `name` field is used to identify the Leaderboard to update. Format: leaderboards/{leaderboard}

    try:
        api_response = api_instance.leaderboard_service_update_leaderboard(leaderboard_name, leaderboard)
        print("The response of LeaderboardServiceApi->leaderboard_service_update_leaderboard:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LeaderboardServiceApi->leaderboard_service_update_leaderboard: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **leaderboard_name** | **str**| Output only. Name of the Leaderboard resource. e.g.: \&quot;leaderboards/&lt;UUID&gt;\&quot; | 
 **leaderboard** | [**RequiredTheLeaderboardToUpdate**](RequiredTheLeaderboardToUpdate.md)| Required. The Leaderboard to update.  The Leaderboard&#39;s &#x60;name&#x60; field is used to identify the Leaderboard to update. Format: leaderboards/{leaderboard} | 

### Return type

[**V1UpdateLeaderboardResponse**](V1UpdateLeaderboardResponse.md)

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

