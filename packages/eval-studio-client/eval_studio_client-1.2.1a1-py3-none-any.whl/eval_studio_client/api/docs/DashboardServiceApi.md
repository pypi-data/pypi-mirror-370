# eval_studio_client.api.DashboardServiceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**dashboard_service_batch_delete_dashboards**](DashboardServiceApi.md#dashboard_service_batch_delete_dashboards) | **POST** /v1/dashboards:batchDelete | 
[**dashboard_service_batch_get_dashboards**](DashboardServiceApi.md#dashboard_service_batch_get_dashboards) | **GET** /v1/dashboards:batchGet | 
[**dashboard_service_create_dashboard**](DashboardServiceApi.md#dashboard_service_create_dashboard) | **POST** /v1/dashboards | 
[**dashboard_service_delete_dashboard**](DashboardServiceApi.md#dashboard_service_delete_dashboard) | **DELETE** /v1/{name} | 
[**dashboard_service_get_dashboard**](DashboardServiceApi.md#dashboard_service_get_dashboard) | **GET** /v1/{name} | 
[**dashboard_service_grant_dashboard_access**](DashboardServiceApi.md#dashboard_service_grant_dashboard_access) | **POST** /v1/{name}:grantAccess | GrantDashboardAccess grants access to a Dashboard to a subject with a specified role.
[**dashboard_service_list_dashboard_access**](DashboardServiceApi.md#dashboard_service_list_dashboard_access) | **GET** /v1/{name}:listAccess | ListDashboardAccess lists access to a Dashboard.
[**dashboard_service_list_dashboards**](DashboardServiceApi.md#dashboard_service_list_dashboards) | **GET** /v1/dashboards | 
[**dashboard_service_list_dashboards_shared_with_me**](DashboardServiceApi.md#dashboard_service_list_dashboards_shared_with_me) | **GET** /v1/dashboards:sharedWithMe | ListDashboardsSharedWithMe lists Dashboards shared with the authenticated user.
[**dashboard_service_list_most_recent_dashboards**](DashboardServiceApi.md#dashboard_service_list_most_recent_dashboards) | **GET** /v1/dashboards:mostRecent | 
[**dashboard_service_revoke_dashboard_access**](DashboardServiceApi.md#dashboard_service_revoke_dashboard_access) | **POST** /v1/{name}:revokeAccess | RevokeDashboardAccess revokes access to a Dashboard from a subject.
[**dashboard_service_update_dashboard**](DashboardServiceApi.md#dashboard_service_update_dashboard) | **PATCH** /v1/{dashboard.name} | 


# **dashboard_service_batch_delete_dashboards**
> V1BatchDeleteDashboardsResponse dashboard_service_batch_delete_dashboards(body)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_batch_delete_dashboards_request import V1BatchDeleteDashboardsRequest
from eval_studio_client.api.models.v1_batch_delete_dashboards_response import V1BatchDeleteDashboardsResponse
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
    api_instance = eval_studio_client.api.DashboardServiceApi(api_client)
    body = eval_studio_client.api.V1BatchDeleteDashboardsRequest() # V1BatchDeleteDashboardsRequest | 

    try:
        api_response = api_instance.dashboard_service_batch_delete_dashboards(body)
        print("The response of DashboardServiceApi->dashboard_service_batch_delete_dashboards:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardServiceApi->dashboard_service_batch_delete_dashboards: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**V1BatchDeleteDashboardsRequest**](V1BatchDeleteDashboardsRequest.md)|  | 

### Return type

[**V1BatchDeleteDashboardsResponse**](V1BatchDeleteDashboardsResponse.md)

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

# **dashboard_service_batch_get_dashboards**
> V1BatchGetDashboardsResponse dashboard_service_batch_get_dashboards(names=names)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_batch_get_dashboards_response import V1BatchGetDashboardsResponse
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
    api_instance = eval_studio_client.api.DashboardServiceApi(api_client)
    names = ['names_example'] # List[str] | Required. The names of the Dashboards to retrieve. A maximum of 1000 can be specified. (optional)

    try:
        api_response = api_instance.dashboard_service_batch_get_dashboards(names=names)
        print("The response of DashboardServiceApi->dashboard_service_batch_get_dashboards:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardServiceApi->dashboard_service_batch_get_dashboards: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **names** | [**List[str]**](str.md)| Required. The names of the Dashboards to retrieve. A maximum of 1000 can be specified. | [optional] 

### Return type

[**V1BatchGetDashboardsResponse**](V1BatchGetDashboardsResponse.md)

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

# **dashboard_service_create_dashboard**
> V1CreateDashboardResponse dashboard_service_create_dashboard(dashboard)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_create_dashboard_response import V1CreateDashboardResponse
from eval_studio_client.api.models.v1_dashboard import V1Dashboard
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
    api_instance = eval_studio_client.api.DashboardServiceApi(api_client)
    dashboard = eval_studio_client.api.V1Dashboard() # V1Dashboard | Required. The Dashboard to create.

    try:
        api_response = api_instance.dashboard_service_create_dashboard(dashboard)
        print("The response of DashboardServiceApi->dashboard_service_create_dashboard:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardServiceApi->dashboard_service_create_dashboard: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dashboard** | [**V1Dashboard**](V1Dashboard.md)| Required. The Dashboard to create. | 

### Return type

[**V1CreateDashboardResponse**](V1CreateDashboardResponse.md)

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

# **dashboard_service_delete_dashboard**
> V1DeleteDashboardResponse dashboard_service_delete_dashboard(name)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_delete_dashboard_response import V1DeleteDashboardResponse
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
    api_instance = eval_studio_client.api.DashboardServiceApi(api_client)
    name = 'name_example' # str | Required. The name of the Dashboard to delete.

    try:
        api_response = api_instance.dashboard_service_delete_dashboard(name)
        print("The response of DashboardServiceApi->dashboard_service_delete_dashboard:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardServiceApi->dashboard_service_delete_dashboard: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Required. The name of the Dashboard to delete. | 

### Return type

[**V1DeleteDashboardResponse**](V1DeleteDashboardResponse.md)

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

# **dashboard_service_get_dashboard**
> V1GetDashboardResponse dashboard_service_get_dashboard(name)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_get_dashboard_response import V1GetDashboardResponse
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
    api_instance = eval_studio_client.api.DashboardServiceApi(api_client)
    name = 'name_example' # str | Required. The name of the Dashboard to retrieve.

    try:
        api_response = api_instance.dashboard_service_get_dashboard(name)
        print("The response of DashboardServiceApi->dashboard_service_get_dashboard:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardServiceApi->dashboard_service_get_dashboard: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Required. The name of the Dashboard to retrieve. | 

### Return type

[**V1GetDashboardResponse**](V1GetDashboardResponse.md)

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

# **dashboard_service_grant_dashboard_access**
> object dashboard_service_grant_dashboard_access(name, body)

GrantDashboardAccess grants access to a Dashboard to a subject with a specified role.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.test_service_grant_test_access_request import TestServiceGrantTestAccessRequest
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
    api_instance = eval_studio_client.api.DashboardServiceApi(api_client)
    name = 'name_example' # str | Required. The name of the Dashboard to grant access to.
    body = eval_studio_client.api.TestServiceGrantTestAccessRequest() # TestServiceGrantTestAccessRequest | 

    try:
        # GrantDashboardAccess grants access to a Dashboard to a subject with a specified role.
        api_response = api_instance.dashboard_service_grant_dashboard_access(name, body)
        print("The response of DashboardServiceApi->dashboard_service_grant_dashboard_access:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardServiceApi->dashboard_service_grant_dashboard_access: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Required. The name of the Dashboard to grant access to. | 
 **body** | [**TestServiceGrantTestAccessRequest**](TestServiceGrantTestAccessRequest.md)|  | 

### Return type

**object**

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

# **dashboard_service_list_dashboard_access**
> V1ListDashboardAccessResponse dashboard_service_list_dashboard_access(name)

ListDashboardAccess lists access to a Dashboard.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_list_dashboard_access_response import V1ListDashboardAccessResponse
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
    api_instance = eval_studio_client.api.DashboardServiceApi(api_client)
    name = 'name_example' # str | Required. The name of the Dashboard to list access for.

    try:
        # ListDashboardAccess lists access to a Dashboard.
        api_response = api_instance.dashboard_service_list_dashboard_access(name)
        print("The response of DashboardServiceApi->dashboard_service_list_dashboard_access:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardServiceApi->dashboard_service_list_dashboard_access: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Required. The name of the Dashboard to list access for. | 

### Return type

[**V1ListDashboardAccessResponse**](V1ListDashboardAccessResponse.md)

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

# **dashboard_service_list_dashboards**
> V1ListDashboardsResponse dashboard_service_list_dashboards(filter=filter)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_list_dashboards_response import V1ListDashboardsResponse
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
    api_instance = eval_studio_client.api.DashboardServiceApi(api_client)
    filter = 'filter_example' # str | Optional. If specified, only dashboards matching the filter will be returned. Attempts to implement AIP-160 (https://aip.dev/160), although not all fields, operators and features are supported.  Supported fields: - models   - only ':' operator (has) is supported (no wildcards), e.g. \"models:\\\"models/<UUID>\\\"\" (optional)

    try:
        api_response = api_instance.dashboard_service_list_dashboards(filter=filter)
        print("The response of DashboardServiceApi->dashboard_service_list_dashboards:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardServiceApi->dashboard_service_list_dashboards: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filter** | **str**| Optional. If specified, only dashboards matching the filter will be returned. Attempts to implement AIP-160 (https://aip.dev/160), although not all fields, operators and features are supported.  Supported fields: - models   - only &#39;:&#39; operator (has) is supported (no wildcards), e.g. \&quot;models:\\\&quot;models/&lt;UUID&gt;\\\&quot;\&quot; | [optional] 

### Return type

[**V1ListDashboardsResponse**](V1ListDashboardsResponse.md)

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

# **dashboard_service_list_dashboards_shared_with_me**
> V1ListDashboardsSharedWithMeResponse dashboard_service_list_dashboards_shared_with_me()

ListDashboardsSharedWithMe lists Dashboards shared with the authenticated user.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_list_dashboards_shared_with_me_response import V1ListDashboardsSharedWithMeResponse
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
    api_instance = eval_studio_client.api.DashboardServiceApi(api_client)

    try:
        # ListDashboardsSharedWithMe lists Dashboards shared with the authenticated user.
        api_response = api_instance.dashboard_service_list_dashboards_shared_with_me()
        print("The response of DashboardServiceApi->dashboard_service_list_dashboards_shared_with_me:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardServiceApi->dashboard_service_list_dashboards_shared_with_me: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**V1ListDashboardsSharedWithMeResponse**](V1ListDashboardsSharedWithMeResponse.md)

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

# **dashboard_service_list_most_recent_dashboards**
> V1ListMostRecentDashboardsResponse dashboard_service_list_most_recent_dashboards(limit=limit, filter=filter)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_list_most_recent_dashboards_response import V1ListMostRecentDashboardsResponse
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
    api_instance = eval_studio_client.api.DashboardServiceApi(api_client)
    limit = 56 # int | Optional. The max number of the most recent Dashboards to retrieve. Use -1 to retrieve all. Defaults to 3. (optional)
    filter = 'filter_example' # str | Optional. If specified, only leaderboards matching the filter will be returned. Attempts to implement AIP-160 (https://aip.dev/160), although not all fields, operators and features are supported.  Supported fields: - model   - only '=' operator is supported, e.g. \"model = \\\"models/<UUID>\\\"\" (optional)

    try:
        api_response = api_instance.dashboard_service_list_most_recent_dashboards(limit=limit, filter=filter)
        print("The response of DashboardServiceApi->dashboard_service_list_most_recent_dashboards:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardServiceApi->dashboard_service_list_most_recent_dashboards: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| Optional. The max number of the most recent Dashboards to retrieve. Use -1 to retrieve all. Defaults to 3. | [optional] 
 **filter** | **str**| Optional. If specified, only leaderboards matching the filter will be returned. Attempts to implement AIP-160 (https://aip.dev/160), although not all fields, operators and features are supported.  Supported fields: - model   - only &#39;&#x3D;&#39; operator is supported, e.g. \&quot;model &#x3D; \\\&quot;models/&lt;UUID&gt;\\\&quot;\&quot; | [optional] 

### Return type

[**V1ListMostRecentDashboardsResponse**](V1ListMostRecentDashboardsResponse.md)

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

# **dashboard_service_revoke_dashboard_access**
> object dashboard_service_revoke_dashboard_access(name, body)

RevokeDashboardAccess revokes access to a Dashboard from a subject.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.workflow_service_revoke_workflow_access_request import WorkflowServiceRevokeWorkflowAccessRequest
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
    api_instance = eval_studio_client.api.DashboardServiceApi(api_client)
    name = 'name_example' # str | Required. The name of the Dashboard to revoke access from.
    body = eval_studio_client.api.WorkflowServiceRevokeWorkflowAccessRequest() # WorkflowServiceRevokeWorkflowAccessRequest | 

    try:
        # RevokeDashboardAccess revokes access to a Dashboard from a subject.
        api_response = api_instance.dashboard_service_revoke_dashboard_access(name, body)
        print("The response of DashboardServiceApi->dashboard_service_revoke_dashboard_access:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardServiceApi->dashboard_service_revoke_dashboard_access: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Required. The name of the Dashboard to revoke access from. | 
 **body** | [**WorkflowServiceRevokeWorkflowAccessRequest**](WorkflowServiceRevokeWorkflowAccessRequest.md)|  | 

### Return type

**object**

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

# **dashboard_service_update_dashboard**
> V1UpdateDashboardResponse dashboard_service_update_dashboard(dashboard_name, dashboard)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.required_the_dashboard_to_update import RequiredTheDashboardToUpdate
from eval_studio_client.api.models.v1_update_dashboard_response import V1UpdateDashboardResponse
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
    api_instance = eval_studio_client.api.DashboardServiceApi(api_client)
    dashboard_name = 'dashboard_name_example' # str | Output only. Name of the Dashboard resource. e.g.: \"dashboards/<UUID>\"
    dashboard = eval_studio_client.api.RequiredTheDashboardToUpdate() # RequiredTheDashboardToUpdate | Required. The Dashboard to update.  The Dashboard's `name` field is used to identify the Dashboard to update. Format: dashboards/{dashboard}

    try:
        api_response = api_instance.dashboard_service_update_dashboard(dashboard_name, dashboard)
        print("The response of DashboardServiceApi->dashboard_service_update_dashboard:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardServiceApi->dashboard_service_update_dashboard: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dashboard_name** | **str**| Output only. Name of the Dashboard resource. e.g.: \&quot;dashboards/&lt;UUID&gt;\&quot; | 
 **dashboard** | [**RequiredTheDashboardToUpdate**](RequiredTheDashboardToUpdate.md)| Required. The Dashboard to update.  The Dashboard&#39;s &#x60;name&#x60; field is used to identify the Dashboard to update. Format: dashboards/{dashboard} | 

### Return type

[**V1UpdateDashboardResponse**](V1UpdateDashboardResponse.md)

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

