# eval_studio_client.api.WorkflowServiceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**workflow_service_batch_delete_workflows**](WorkflowServiceApi.md#workflow_service_batch_delete_workflows) | **POST** /v1/workflows:batchDelete | BatchDeleteWorkflows deletes Workflows by names. If any of the Workflows do not exist an error is returned.
[**workflow_service_clone_workflow**](WorkflowServiceApi.md#workflow_service_clone_workflow) | **POST** /v1/{name_1}:clone | CloneWorkflow clones an existing Workflow.
[**workflow_service_create_workflow**](WorkflowServiceApi.md#workflow_service_create_workflow) | **POST** /v1/workflows | CreateWorkflow creates a Workflow.
[**workflow_service_delete_workflow**](WorkflowServiceApi.md#workflow_service_delete_workflow) | **DELETE** /v1/{name_9} | DeleteWorkflow deletes a Workflow by name. If the Workflow does not exist an error is returned.
[**workflow_service_find_workflows_by_collection_id**](WorkflowServiceApi.md#workflow_service_find_workflows_by_collection_id) | **GET** /v1/workflows:findWorkflowByH2OGPTeCollectionID | FindWorkflowByCollectionID finds a Workflow by used H2OGPTe collection ID.
[**workflow_service_get_guardrails_configuration**](WorkflowServiceApi.md#workflow_service_get_guardrails_configuration) | **GET** /v1/{name}:getGuardrailsConfiguration | 
[**workflow_service_get_workflow**](WorkflowServiceApi.md#workflow_service_get_workflow) | **GET** /v1/{name_12} | GetWorkflow retrieves a Workflow by name. Deleted Workflow is returned without error, it has a delete_time and deleter fields set.
[**workflow_service_grant_workflow_access**](WorkflowServiceApi.md#workflow_service_grant_workflow_access) | **POST** /v1/{name_2}:grantAccess | GrantWorkflowAccess grants access to a Workflow to a subject with a specified role.
[**workflow_service_list_workflow_access**](WorkflowServiceApi.md#workflow_service_list_workflow_access) | **GET** /v1/{name_2}:listAccess | ListWorkflowAccess lists access to a Workflow.
[**workflow_service_list_workflow_dependencies**](WorkflowServiceApi.md#workflow_service_list_workflow_dependencies) | **GET** /v1/{name}:nodeDependencies | ListWorkflowDependencies lists workflow nodes and map of the node dependencies.
[**workflow_service_list_workflows**](WorkflowServiceApi.md#workflow_service_list_workflows) | **GET** /v1/workflows | ListWorkflows lists Workflows.
[**workflow_service_list_workflows_shared_with_me**](WorkflowServiceApi.md#workflow_service_list_workflows_shared_with_me) | **GET** /v1/workflows:sharedWithMe | ListWorkflowsSharedWithMe lists Workflows shared with the authenticated user.
[**workflow_service_revoke_workflow_access**](WorkflowServiceApi.md#workflow_service_revoke_workflow_access) | **POST** /v1/{name_2}:revokeAccess | RevokeWorkflowAccess revokes access to a Workflow from a subject.
[**workflow_service_update_workflow**](WorkflowServiceApi.md#workflow_service_update_workflow) | **PATCH** /v1/{workflow.name} | UpdateWorkflow updates a Workflow. The update_mask is used to specify the fields to be updated.


# **workflow_service_batch_delete_workflows**
> V1BatchDeleteWorkflowsResponse workflow_service_batch_delete_workflows(body)

BatchDeleteWorkflows deletes Workflows by names. If any of the Workflows do not exist an error is returned.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_batch_delete_workflows_request import V1BatchDeleteWorkflowsRequest
from eval_studio_client.api.models.v1_batch_delete_workflows_response import V1BatchDeleteWorkflowsResponse
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
    api_instance = eval_studio_client.api.WorkflowServiceApi(api_client)
    body = eval_studio_client.api.V1BatchDeleteWorkflowsRequest() # V1BatchDeleteWorkflowsRequest | 

    try:
        # BatchDeleteWorkflows deletes Workflows by names. If any of the Workflows do not exist an error is returned.
        api_response = api_instance.workflow_service_batch_delete_workflows(body)
        print("The response of WorkflowServiceApi->workflow_service_batch_delete_workflows:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowServiceApi->workflow_service_batch_delete_workflows: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**V1BatchDeleteWorkflowsRequest**](V1BatchDeleteWorkflowsRequest.md)|  | 

### Return type

[**V1BatchDeleteWorkflowsResponse**](V1BatchDeleteWorkflowsResponse.md)

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

# **workflow_service_clone_workflow**
> V1CloneWorkflowResponse workflow_service_clone_workflow(name_1, body)

CloneWorkflow clones an existing Workflow.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_clone_workflow_response import V1CloneWorkflowResponse
from eval_studio_client.api.models.workflow_service_clone_workflow_request import WorkflowServiceCloneWorkflowRequest
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
    api_instance = eval_studio_client.api.WorkflowServiceApi(api_client)
    name_1 = 'name_1_example' # str | Required. The name of the Workflow to clone.
    body = eval_studio_client.api.WorkflowServiceCloneWorkflowRequest() # WorkflowServiceCloneWorkflowRequest | 

    try:
        # CloneWorkflow clones an existing Workflow.
        api_response = api_instance.workflow_service_clone_workflow(name_1, body)
        print("The response of WorkflowServiceApi->workflow_service_clone_workflow:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowServiceApi->workflow_service_clone_workflow: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name_1** | **str**| Required. The name of the Workflow to clone. | 
 **body** | [**WorkflowServiceCloneWorkflowRequest**](WorkflowServiceCloneWorkflowRequest.md)|  | 

### Return type

[**V1CloneWorkflowResponse**](V1CloneWorkflowResponse.md)

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

# **workflow_service_create_workflow**
> V1CreateWorkflowResponse workflow_service_create_workflow(workflow)

CreateWorkflow creates a Workflow.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_create_workflow_response import V1CreateWorkflowResponse
from eval_studio_client.api.models.v1_workflow import V1Workflow
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
    api_instance = eval_studio_client.api.WorkflowServiceApi(api_client)
    workflow = eval_studio_client.api.V1Workflow() # V1Workflow | Required. The Workflow to create.

    try:
        # CreateWorkflow creates a Workflow.
        api_response = api_instance.workflow_service_create_workflow(workflow)
        print("The response of WorkflowServiceApi->workflow_service_create_workflow:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowServiceApi->workflow_service_create_workflow: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow** | [**V1Workflow**](V1Workflow.md)| Required. The Workflow to create. | 

### Return type

[**V1CreateWorkflowResponse**](V1CreateWorkflowResponse.md)

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

# **workflow_service_delete_workflow**
> V1DeleteWorkflowResponse workflow_service_delete_workflow(name_9)

DeleteWorkflow deletes a Workflow by name. If the Workflow does not exist an error is returned.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_delete_workflow_response import V1DeleteWorkflowResponse
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
    api_instance = eval_studio_client.api.WorkflowServiceApi(api_client)
    name_9 = 'name_9_example' # str | Required. The name of the Workflow to delete.

    try:
        # DeleteWorkflow deletes a Workflow by name. If the Workflow does not exist an error is returned.
        api_response = api_instance.workflow_service_delete_workflow(name_9)
        print("The response of WorkflowServiceApi->workflow_service_delete_workflow:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowServiceApi->workflow_service_delete_workflow: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name_9** | **str**| Required. The name of the Workflow to delete. | 

### Return type

[**V1DeleteWorkflowResponse**](V1DeleteWorkflowResponse.md)

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

# **workflow_service_find_workflows_by_collection_id**
> V1FindWorkflowsByCollectionIDResponse workflow_service_find_workflows_by_collection_id(collection_id=collection_id)

FindWorkflowByCollectionID finds a Workflow by used H2OGPTe collection ID.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_find_workflows_by_collection_id_response import V1FindWorkflowsByCollectionIDResponse
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
    api_instance = eval_studio_client.api.WorkflowServiceApi(api_client)
    collection_id = 'collection_id_example' # str | Required. The H2OGPTe collection ID to find the Workflow by. (optional)

    try:
        # FindWorkflowByCollectionID finds a Workflow by used H2OGPTe collection ID.
        api_response = api_instance.workflow_service_find_workflows_by_collection_id(collection_id=collection_id)
        print("The response of WorkflowServiceApi->workflow_service_find_workflows_by_collection_id:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowServiceApi->workflow_service_find_workflows_by_collection_id: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_id** | **str**| Required. The H2OGPTe collection ID to find the Workflow by. | [optional] 

### Return type

[**V1FindWorkflowsByCollectionIDResponse**](V1FindWorkflowsByCollectionIDResponse.md)

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

# **workflow_service_get_guardrails_configuration**
> V1GetGuardrailsConfigurationResponse workflow_service_get_guardrails_configuration(name)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_get_guardrails_configuration_response import V1GetGuardrailsConfigurationResponse
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
    api_instance = eval_studio_client.api.WorkflowServiceApi(api_client)
    name = 'name_example' # str | Required. The name of the Workflow to retrieve guardrails configuration for. The Human Calibration node must be completed, otherwise an error is returned.

    try:
        api_response = api_instance.workflow_service_get_guardrails_configuration(name)
        print("The response of WorkflowServiceApi->workflow_service_get_guardrails_configuration:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowServiceApi->workflow_service_get_guardrails_configuration: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Required. The name of the Workflow to retrieve guardrails configuration for. The Human Calibration node must be completed, otherwise an error is returned. | 

### Return type

[**V1GetGuardrailsConfigurationResponse**](V1GetGuardrailsConfigurationResponse.md)

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

# **workflow_service_get_workflow**
> V1GetWorkflowResponse workflow_service_get_workflow(name_12)

GetWorkflow retrieves a Workflow by name. Deleted Workflow is returned without error, it has a delete_time and deleter fields set.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_get_workflow_response import V1GetWorkflowResponse
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
    api_instance = eval_studio_client.api.WorkflowServiceApi(api_client)
    name_12 = 'name_12_example' # str | Required. The name of the Workflow to retrieve.

    try:
        # GetWorkflow retrieves a Workflow by name. Deleted Workflow is returned without error, it has a delete_time and deleter fields set.
        api_response = api_instance.workflow_service_get_workflow(name_12)
        print("The response of WorkflowServiceApi->workflow_service_get_workflow:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowServiceApi->workflow_service_get_workflow: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name_12** | **str**| Required. The name of the Workflow to retrieve. | 

### Return type

[**V1GetWorkflowResponse**](V1GetWorkflowResponse.md)

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

# **workflow_service_grant_workflow_access**
> object workflow_service_grant_workflow_access(name_2, body)

GrantWorkflowAccess grants access to a Workflow to a subject with a specified role.

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
    api_instance = eval_studio_client.api.WorkflowServiceApi(api_client)
    name_2 = 'name_2_example' # str | Required. The name of the Workflow to grant access to.
    body = eval_studio_client.api.TestServiceGrantTestAccessRequest() # TestServiceGrantTestAccessRequest | 

    try:
        # GrantWorkflowAccess grants access to a Workflow to a subject with a specified role.
        api_response = api_instance.workflow_service_grant_workflow_access(name_2, body)
        print("The response of WorkflowServiceApi->workflow_service_grant_workflow_access:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowServiceApi->workflow_service_grant_workflow_access: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name_2** | **str**| Required. The name of the Workflow to grant access to. | 
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

# **workflow_service_list_workflow_access**
> V1ListWorkflowAccessResponse workflow_service_list_workflow_access(name_2)

ListWorkflowAccess lists access to a Workflow.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_list_workflow_access_response import V1ListWorkflowAccessResponse
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
    api_instance = eval_studio_client.api.WorkflowServiceApi(api_client)
    name_2 = 'name_2_example' # str | Required. The name of the Workflow to list access for.

    try:
        # ListWorkflowAccess lists access to a Workflow.
        api_response = api_instance.workflow_service_list_workflow_access(name_2)
        print("The response of WorkflowServiceApi->workflow_service_list_workflow_access:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowServiceApi->workflow_service_list_workflow_access: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name_2** | **str**| Required. The name of the Workflow to list access for. | 

### Return type

[**V1ListWorkflowAccessResponse**](V1ListWorkflowAccessResponse.md)

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

# **workflow_service_list_workflow_dependencies**
> V1ListWorkflowDependenciesResponse workflow_service_list_workflow_dependencies(name)

ListWorkflowDependencies lists workflow nodes and map of the node dependencies.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_list_workflow_dependencies_response import V1ListWorkflowDependenciesResponse
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
    api_instance = eval_studio_client.api.WorkflowServiceApi(api_client)
    name = 'name_example' # str | Required. The name of the Workflow to retrieve dependencies for.

    try:
        # ListWorkflowDependencies lists workflow nodes and map of the node dependencies.
        api_response = api_instance.workflow_service_list_workflow_dependencies(name)
        print("The response of WorkflowServiceApi->workflow_service_list_workflow_dependencies:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowServiceApi->workflow_service_list_workflow_dependencies: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Required. The name of the Workflow to retrieve dependencies for. | 

### Return type

[**V1ListWorkflowDependenciesResponse**](V1ListWorkflowDependenciesResponse.md)

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

# **workflow_service_list_workflows**
> V1ListWorkflowsResponse workflow_service_list_workflows()

ListWorkflows lists Workflows.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_list_workflows_response import V1ListWorkflowsResponse
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
    api_instance = eval_studio_client.api.WorkflowServiceApi(api_client)

    try:
        # ListWorkflows lists Workflows.
        api_response = api_instance.workflow_service_list_workflows()
        print("The response of WorkflowServiceApi->workflow_service_list_workflows:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowServiceApi->workflow_service_list_workflows: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**V1ListWorkflowsResponse**](V1ListWorkflowsResponse.md)

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

# **workflow_service_list_workflows_shared_with_me**
> V1ListWorkflowsSharedWithMeResponse workflow_service_list_workflows_shared_with_me()

ListWorkflowsSharedWithMe lists Workflows shared with the authenticated user.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_list_workflows_shared_with_me_response import V1ListWorkflowsSharedWithMeResponse
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
    api_instance = eval_studio_client.api.WorkflowServiceApi(api_client)

    try:
        # ListWorkflowsSharedWithMe lists Workflows shared with the authenticated user.
        api_response = api_instance.workflow_service_list_workflows_shared_with_me()
        print("The response of WorkflowServiceApi->workflow_service_list_workflows_shared_with_me:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowServiceApi->workflow_service_list_workflows_shared_with_me: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**V1ListWorkflowsSharedWithMeResponse**](V1ListWorkflowsSharedWithMeResponse.md)

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

# **workflow_service_revoke_workflow_access**
> object workflow_service_revoke_workflow_access(name_2, body)

RevokeWorkflowAccess revokes access to a Workflow from a subject.

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
    api_instance = eval_studio_client.api.WorkflowServiceApi(api_client)
    name_2 = 'name_2_example' # str | Required. The name of the Workflow to revoke access from.
    body = eval_studio_client.api.WorkflowServiceRevokeWorkflowAccessRequest() # WorkflowServiceRevokeWorkflowAccessRequest | 

    try:
        # RevokeWorkflowAccess revokes access to a Workflow from a subject.
        api_response = api_instance.workflow_service_revoke_workflow_access(name_2, body)
        print("The response of WorkflowServiceApi->workflow_service_revoke_workflow_access:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowServiceApi->workflow_service_revoke_workflow_access: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name_2** | **str**| Required. The name of the Workflow to revoke access from. | 
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

# **workflow_service_update_workflow**
> V1UpdateWorkflowResponse workflow_service_update_workflow(workflow_name, workflow)

UpdateWorkflow updates a Workflow. The update_mask is used to specify the fields to be updated.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.required_the_updated_workflow import RequiredTheUpdatedWorkflow
from eval_studio_client.api.models.v1_update_workflow_response import V1UpdateWorkflowResponse
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
    api_instance = eval_studio_client.api.WorkflowServiceApi(api_client)
    workflow_name = 'workflow_name_example' # str | Output only. Immutable. Resource name of the Workflow in format of `workflows/{workflow_id}`.
    workflow = eval_studio_client.api.RequiredTheUpdatedWorkflow() # RequiredTheUpdatedWorkflow | Required. The updated Workflow.

    try:
        # UpdateWorkflow updates a Workflow. The update_mask is used to specify the fields to be updated.
        api_response = api_instance.workflow_service_update_workflow(workflow_name, workflow)
        print("The response of WorkflowServiceApi->workflow_service_update_workflow:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowServiceApi->workflow_service_update_workflow: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow_name** | **str**| Output only. Immutable. Resource name of the Workflow in format of &#x60;workflows/{workflow_id}&#x60;. | 
 **workflow** | [**RequiredTheUpdatedWorkflow**](RequiredTheUpdatedWorkflow.md)| Required. The updated Workflow. | 

### Return type

[**V1UpdateWorkflowResponse**](V1UpdateWorkflowResponse.md)

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

