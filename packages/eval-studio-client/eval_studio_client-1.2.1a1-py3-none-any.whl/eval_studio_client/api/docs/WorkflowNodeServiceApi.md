# eval_studio_client.api.WorkflowNodeServiceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**workflow_node_service_batch_get_workflow_nodes**](WorkflowNodeServiceApi.md#workflow_node_service_batch_get_workflow_nodes) | **GET** /v1/workflows/*/nodes:batchGet | BatchGetWorkflowNodes retrieves all WorkflowNodes with the specified resource names. If any of the WorkflowNodes do not exist an error is returned. Deleted WorkflowNodes are returned without error. The order of resource names in the request and the returned WorkflowNodes might differ.
[**workflow_node_service_create_workflow_node**](WorkflowNodeServiceApi.md#workflow_node_service_create_workflow_node) | **POST** /v1/{parent}/nodes | CreateWorkflowNode creates a new WorkflowNode.
[**workflow_node_service_delete_workflow_node**](WorkflowNodeServiceApi.md#workflow_node_service_delete_workflow_node) | **DELETE** /v1/{name_8} | DeleteWorkflowNode deletes a WorkflowNode by name. If the WorkflowNode does not exist an error is returned. The edges are handled in a following way:
[**workflow_node_service_get_workflow_node**](WorkflowNodeServiceApi.md#workflow_node_service_get_workflow_node) | **GET** /v1/{name_11} | GetWorkflowNode retrieves a WorkflowNode by name. Deleted WorkflowNode is returned without error, it has a delete_time and deleter fields set.
[**workflow_node_service_get_workflow_node_prerequisites**](WorkflowNodeServiceApi.md#workflow_node_service_get_workflow_node_prerequisites) | **GET** /v1/{name}:getPrerequisites | GetWorkflowNodePrerequisites retrieves the WorkflowNodes and WorkflowEdges that are the prerequisites of the specified WorkflowNode. The list might be empty. Large data might be stored in storage and not returned in the response. It is client&#39;s responsibility to retrieve the data from storage using the content handlers. It is intended to be used by the Eval Studio Workers.
[**workflow_node_service_init_workflow_node**](WorkflowNodeServiceApi.md#workflow_node_service_init_workflow_node) | **POST** /v1/{name}:init | InitWorkflowNode initializes a WorkflowNode on first access.
[**workflow_node_service_process_workflow_node**](WorkflowNodeServiceApi.md#workflow_node_service_process_workflow_node) | **POST** /v1/{name}:process | ProcessWorkflowNode processes a WorkflowNode.
[**workflow_node_service_reset_workflow_node**](WorkflowNodeServiceApi.md#workflow_node_service_reset_workflow_node) | **POST** /v1/{name}:reset | ResetWorkflowNode resets a WorkflowNode.
[**workflow_node_service_update_workflow_node**](WorkflowNodeServiceApi.md#workflow_node_service_update_workflow_node) | **PATCH** /v1/{node.name} | UpdateWorkflowNode updates a WorkflowNode. The update_mask is used to specify the fields to be updated.


# **workflow_node_service_batch_get_workflow_nodes**
> V1BatchGetWorkflowNodesResponse workflow_node_service_batch_get_workflow_nodes(names=names, view=view)

BatchGetWorkflowNodes retrieves all WorkflowNodes with the specified resource names. If any of the WorkflowNodes do not exist an error is returned. Deleted WorkflowNodes are returned without error. The order of resource names in the request and the returned WorkflowNodes might differ.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_batch_get_workflow_nodes_response import V1BatchGetWorkflowNodesResponse
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
    api_instance = eval_studio_client.api.WorkflowNodeServiceApi(api_client)
    names = ['names_example'] # List[str] | Required. The resource names of the WorkflowNodes to retrieve. Maximum 1000 items. (optional)
    view = 'WORKFLOW_NODE_VIEW_UNSPECIFIED' # str | Optional. The level of detail to include in the response.   - WORKFLOW_NODE_VIEW_UNSPECIFIED: Unspecified view.  - WORKFLOW_NODE_VIEW_BASIC: Basic view. Lacks large data fields. TODO: describe what fields are omitted.  - WORKFLOW_NODE_VIEW_FULL: Full view. Contains all fields. (optional) (default to 'WORKFLOW_NODE_VIEW_UNSPECIFIED')

    try:
        # BatchGetWorkflowNodes retrieves all WorkflowNodes with the specified resource names. If any of the WorkflowNodes do not exist an error is returned. Deleted WorkflowNodes are returned without error. The order of resource names in the request and the returned WorkflowNodes might differ.
        api_response = api_instance.workflow_node_service_batch_get_workflow_nodes(names=names, view=view)
        print("The response of WorkflowNodeServiceApi->workflow_node_service_batch_get_workflow_nodes:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowNodeServiceApi->workflow_node_service_batch_get_workflow_nodes: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **names** | [**List[str]**](str.md)| Required. The resource names of the WorkflowNodes to retrieve. Maximum 1000 items. | [optional] 
 **view** | **str**| Optional. The level of detail to include in the response.   - WORKFLOW_NODE_VIEW_UNSPECIFIED: Unspecified view.  - WORKFLOW_NODE_VIEW_BASIC: Basic view. Lacks large data fields. TODO: describe what fields are omitted.  - WORKFLOW_NODE_VIEW_FULL: Full view. Contains all fields. | [optional] [default to &#39;WORKFLOW_NODE_VIEW_UNSPECIFIED&#39;]

### Return type

[**V1BatchGetWorkflowNodesResponse**](V1BatchGetWorkflowNodesResponse.md)

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

# **workflow_node_service_create_workflow_node**
> V1CreateWorkflowNodeResponse workflow_node_service_create_workflow_node(parent, node)

CreateWorkflowNode creates a new WorkflowNode.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_create_workflow_node_response import V1CreateWorkflowNodeResponse
from eval_studio_client.api.models.v1_workflow_node import V1WorkflowNode
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
    api_instance = eval_studio_client.api.WorkflowNodeServiceApi(api_client)
    parent = 'parent_example' # str | Required. The parent Workflow in format of `workflow/{workflow_id}`.
    node = eval_studio_client.api.V1WorkflowNode() # V1WorkflowNode | Required. The WorkflowNode to create.

    try:
        # CreateWorkflowNode creates a new WorkflowNode.
        api_response = api_instance.workflow_node_service_create_workflow_node(parent, node)
        print("The response of WorkflowNodeServiceApi->workflow_node_service_create_workflow_node:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowNodeServiceApi->workflow_node_service_create_workflow_node: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **parent** | **str**| Required. The parent Workflow in format of &#x60;workflow/{workflow_id}&#x60;. | 
 **node** | [**V1WorkflowNode**](V1WorkflowNode.md)| Required. The WorkflowNode to create. | 

### Return type

[**V1CreateWorkflowNodeResponse**](V1CreateWorkflowNodeResponse.md)

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

# **workflow_node_service_delete_workflow_node**
> V1DeleteWorkflowNodeResponse workflow_node_service_delete_workflow_node(name_8)

DeleteWorkflowNode deletes a WorkflowNode by name. If the WorkflowNode does not exist an error is returned. The edges are handled in a following way:

- inbound edges are deleted - for every outbound edge a new edge is created for every inbound node and the given   outbound node  For example, deleting node D in the following graph:   A ⇾ B ⇾ D ⇾ E     ↘   ↗       C would create the following:   A ⇾ B ⇾ E     ↘   ↗       C Deleting node B in the same graph, would create:   A   ⇾   D ⇾ E     ↘   ↗       C

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_delete_workflow_node_response import V1DeleteWorkflowNodeResponse
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
    api_instance = eval_studio_client.api.WorkflowNodeServiceApi(api_client)
    name_8 = 'name_8_example' # str | Required. The name of the WorkflowNode to delete.

    try:
        # DeleteWorkflowNode deletes a WorkflowNode by name. If the WorkflowNode does not exist an error is returned. The edges are handled in a following way:
        api_response = api_instance.workflow_node_service_delete_workflow_node(name_8)
        print("The response of WorkflowNodeServiceApi->workflow_node_service_delete_workflow_node:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowNodeServiceApi->workflow_node_service_delete_workflow_node: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name_8** | **str**| Required. The name of the WorkflowNode to delete. | 

### Return type

[**V1DeleteWorkflowNodeResponse**](V1DeleteWorkflowNodeResponse.md)

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

# **workflow_node_service_get_workflow_node**
> V1GetWorkflowNodeResponse workflow_node_service_get_workflow_node(name_11, view=view)

GetWorkflowNode retrieves a WorkflowNode by name. Deleted WorkflowNode is returned without error, it has a delete_time and deleter fields set.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_get_workflow_node_response import V1GetWorkflowNodeResponse
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
    api_instance = eval_studio_client.api.WorkflowNodeServiceApi(api_client)
    name_11 = 'name_11_example' # str | Required. The name of the WorkflowNode to retrieve.
    view = 'WORKFLOW_NODE_VIEW_UNSPECIFIED' # str | Optional. The level of detail to include in the response.   - WORKFLOW_NODE_VIEW_UNSPECIFIED: Unspecified view.  - WORKFLOW_NODE_VIEW_BASIC: Basic view. Lacks large data fields. TODO: describe what fields are omitted.  - WORKFLOW_NODE_VIEW_FULL: Full view. Contains all fields. (optional) (default to 'WORKFLOW_NODE_VIEW_UNSPECIFIED')

    try:
        # GetWorkflowNode retrieves a WorkflowNode by name. Deleted WorkflowNode is returned without error, it has a delete_time and deleter fields set.
        api_response = api_instance.workflow_node_service_get_workflow_node(name_11, view=view)
        print("The response of WorkflowNodeServiceApi->workflow_node_service_get_workflow_node:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowNodeServiceApi->workflow_node_service_get_workflow_node: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name_11** | **str**| Required. The name of the WorkflowNode to retrieve. | 
 **view** | **str**| Optional. The level of detail to include in the response.   - WORKFLOW_NODE_VIEW_UNSPECIFIED: Unspecified view.  - WORKFLOW_NODE_VIEW_BASIC: Basic view. Lacks large data fields. TODO: describe what fields are omitted.  - WORKFLOW_NODE_VIEW_FULL: Full view. Contains all fields. | [optional] [default to &#39;WORKFLOW_NODE_VIEW_UNSPECIFIED&#39;]

### Return type

[**V1GetWorkflowNodeResponse**](V1GetWorkflowNodeResponse.md)

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

# **workflow_node_service_get_workflow_node_prerequisites**
> V1GetWorkflowNodePrerequisitesResponse workflow_node_service_get_workflow_node_prerequisites(name)

GetWorkflowNodePrerequisites retrieves the WorkflowNodes and WorkflowEdges that are the prerequisites of the specified WorkflowNode. The list might be empty. Large data might be stored in storage and not returned in the response. It is client's responsibility to retrieve the data from storage using the content handlers. It is intended to be used by the Eval Studio Workers.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_get_workflow_node_prerequisites_response import V1GetWorkflowNodePrerequisitesResponse
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
    api_instance = eval_studio_client.api.WorkflowNodeServiceApi(api_client)
    name = 'name_example' # str | Required. The name of the WorkflowNode to retrieve the prerequisites for.

    try:
        # GetWorkflowNodePrerequisites retrieves the WorkflowNodes and WorkflowEdges that are the prerequisites of the specified WorkflowNode. The list might be empty. Large data might be stored in storage and not returned in the response. It is client's responsibility to retrieve the data from storage using the content handlers. It is intended to be used by the Eval Studio Workers.
        api_response = api_instance.workflow_node_service_get_workflow_node_prerequisites(name)
        print("The response of WorkflowNodeServiceApi->workflow_node_service_get_workflow_node_prerequisites:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowNodeServiceApi->workflow_node_service_get_workflow_node_prerequisites: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Required. The name of the WorkflowNode to retrieve the prerequisites for. | 

### Return type

[**V1GetWorkflowNodePrerequisitesResponse**](V1GetWorkflowNodePrerequisitesResponse.md)

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

# **workflow_node_service_init_workflow_node**
> V1InitWorkflowNodeResponse workflow_node_service_init_workflow_node(name)

InitWorkflowNode initializes a WorkflowNode on first access.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_init_workflow_node_response import V1InitWorkflowNodeResponse
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
    api_instance = eval_studio_client.api.WorkflowNodeServiceApi(api_client)
    name = 'name_example' # str | Required. The name of the WorkflowNode to initialize.

    try:
        # InitWorkflowNode initializes a WorkflowNode on first access.
        api_response = api_instance.workflow_node_service_init_workflow_node(name)
        print("The response of WorkflowNodeServiceApi->workflow_node_service_init_workflow_node:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowNodeServiceApi->workflow_node_service_init_workflow_node: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Required. The name of the WorkflowNode to initialize. | 

### Return type

[**V1InitWorkflowNodeResponse**](V1InitWorkflowNodeResponse.md)

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

# **workflow_node_service_process_workflow_node**
> V1ProcessWorkflowNodeResponse workflow_node_service_process_workflow_node(name)

ProcessWorkflowNode processes a WorkflowNode.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_process_workflow_node_response import V1ProcessWorkflowNodeResponse
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
    api_instance = eval_studio_client.api.WorkflowNodeServiceApi(api_client)
    name = 'name_example' # str | Required. The name of the WorkflowNode to process.

    try:
        # ProcessWorkflowNode processes a WorkflowNode.
        api_response = api_instance.workflow_node_service_process_workflow_node(name)
        print("The response of WorkflowNodeServiceApi->workflow_node_service_process_workflow_node:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowNodeServiceApi->workflow_node_service_process_workflow_node: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Required. The name of the WorkflowNode to process. | 

### Return type

[**V1ProcessWorkflowNodeResponse**](V1ProcessWorkflowNodeResponse.md)

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

# **workflow_node_service_reset_workflow_node**
> V1ResetWorkflowNodeResponse workflow_node_service_reset_workflow_node(name)

ResetWorkflowNode resets a WorkflowNode.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_reset_workflow_node_response import V1ResetWorkflowNodeResponse
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
    api_instance = eval_studio_client.api.WorkflowNodeServiceApi(api_client)
    name = 'name_example' # str | Required. The name of the WorkflowNode to reset.

    try:
        # ResetWorkflowNode resets a WorkflowNode.
        api_response = api_instance.workflow_node_service_reset_workflow_node(name)
        print("The response of WorkflowNodeServiceApi->workflow_node_service_reset_workflow_node:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowNodeServiceApi->workflow_node_service_reset_workflow_node: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Required. The name of the WorkflowNode to reset. | 

### Return type

[**V1ResetWorkflowNodeResponse**](V1ResetWorkflowNodeResponse.md)

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

# **workflow_node_service_update_workflow_node**
> V1UpdateWorkflowNodeResponse workflow_node_service_update_workflow_node(node_name, node)

UpdateWorkflowNode updates a WorkflowNode. The update_mask is used to specify the fields to be updated.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.required_the_updated_workflow_node import RequiredTheUpdatedWorkflowNode
from eval_studio_client.api.models.v1_update_workflow_node_response import V1UpdateWorkflowNodeResponse
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
    api_instance = eval_studio_client.api.WorkflowNodeServiceApi(api_client)
    node_name = 'node_name_example' # str | Output only. Immutable. Resource name of the Workflow in format of `workflows/{workflow_id}/nodes/{node_id}`.
    node = eval_studio_client.api.RequiredTheUpdatedWorkflowNode() # RequiredTheUpdatedWorkflowNode | Required. The updated WorkflowNode.

    try:
        # UpdateWorkflowNode updates a WorkflowNode. The update_mask is used to specify the fields to be updated.
        api_response = api_instance.workflow_node_service_update_workflow_node(node_name, node)
        print("The response of WorkflowNodeServiceApi->workflow_node_service_update_workflow_node:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowNodeServiceApi->workflow_node_service_update_workflow_node: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **node_name** | **str**| Output only. Immutable. Resource name of the Workflow in format of &#x60;workflows/{workflow_id}/nodes/{node_id}&#x60;. | 
 **node** | [**RequiredTheUpdatedWorkflowNode**](RequiredTheUpdatedWorkflowNode.md)| Required. The updated WorkflowNode. | 

### Return type

[**V1UpdateWorkflowNodeResponse**](V1UpdateWorkflowNodeResponse.md)

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

