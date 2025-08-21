# eval_studio_client.api.WorkflowEdgeServiceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**workflow_edge_service_batch_get_workflow_edges**](WorkflowEdgeServiceApi.md#workflow_edge_service_batch_get_workflow_edges) | **GET** /v1/workflows/*/edges:batchGet | Retrieves all WorkflowEdges with the specified resource names. If any of the WorkflowEdges do not exist an error is returned. The order of resource names in the request and the returned WorkflowEdges might differ.
[**workflow_edge_service_create_workflow_edge**](WorkflowEdgeServiceApi.md#workflow_edge_service_create_workflow_edge) | **POST** /v1/{parent}/edges | CreateWorkflowEdge creates a new WorkflowEdge.
[**workflow_edge_service_delete_workflow_edge**](WorkflowEdgeServiceApi.md#workflow_edge_service_delete_workflow_edge) | **DELETE** /v1/{name_7} | DeleteWorkflowEdge deletes a WorkflowEdge. If the WorkflowEdge does not exist an error is returned


# **workflow_edge_service_batch_get_workflow_edges**
> V1BatchGetWorkflowEdgesResponse workflow_edge_service_batch_get_workflow_edges(names=names)

Retrieves all WorkflowEdges with the specified resource names. If any of the WorkflowEdges do not exist an error is returned. The order of resource names in the request and the returned WorkflowEdges might differ.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_batch_get_workflow_edges_response import V1BatchGetWorkflowEdgesResponse
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
    api_instance = eval_studio_client.api.WorkflowEdgeServiceApi(api_client)
    names = ['names_example'] # List[str] | Required. The resource names of the WorkflowEdges to retrieve. Maximum 1000 items. (optional)

    try:
        # Retrieves all WorkflowEdges with the specified resource names. If any of the WorkflowEdges do not exist an error is returned. The order of resource names in the request and the returned WorkflowEdges might differ.
        api_response = api_instance.workflow_edge_service_batch_get_workflow_edges(names=names)
        print("The response of WorkflowEdgeServiceApi->workflow_edge_service_batch_get_workflow_edges:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowEdgeServiceApi->workflow_edge_service_batch_get_workflow_edges: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **names** | [**List[str]**](str.md)| Required. The resource names of the WorkflowEdges to retrieve. Maximum 1000 items. | [optional] 

### Return type

[**V1BatchGetWorkflowEdgesResponse**](V1BatchGetWorkflowEdgesResponse.md)

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

# **workflow_edge_service_create_workflow_edge**
> V1CreateWorkflowEdgeResponse workflow_edge_service_create_workflow_edge(parent, edge)

CreateWorkflowEdge creates a new WorkflowEdge.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_create_workflow_edge_response import V1CreateWorkflowEdgeResponse
from eval_studio_client.api.models.v1_workflow_edge import V1WorkflowEdge
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
    api_instance = eval_studio_client.api.WorkflowEdgeServiceApi(api_client)
    parent = 'parent_example' # str | Required. The parent Workflow in format of `workflow/{workflow_id}`.
    edge = eval_studio_client.api.V1WorkflowEdge() # V1WorkflowEdge | Required. The WorkflowEdge to create.

    try:
        # CreateWorkflowEdge creates a new WorkflowEdge.
        api_response = api_instance.workflow_edge_service_create_workflow_edge(parent, edge)
        print("The response of WorkflowEdgeServiceApi->workflow_edge_service_create_workflow_edge:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowEdgeServiceApi->workflow_edge_service_create_workflow_edge: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **parent** | **str**| Required. The parent Workflow in format of &#x60;workflow/{workflow_id}&#x60;. | 
 **edge** | [**V1WorkflowEdge**](V1WorkflowEdge.md)| Required. The WorkflowEdge to create. | 

### Return type

[**V1CreateWorkflowEdgeResponse**](V1CreateWorkflowEdgeResponse.md)

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

# **workflow_edge_service_delete_workflow_edge**
> V1DeleteWorkflowEdgeResponse workflow_edge_service_delete_workflow_edge(name_7)

DeleteWorkflowEdge deletes a WorkflowEdge. If the WorkflowEdge does not exist an error is returned

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_delete_workflow_edge_response import V1DeleteWorkflowEdgeResponse
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
    api_instance = eval_studio_client.api.WorkflowEdgeServiceApi(api_client)
    name_7 = 'name_7_example' # str | Required. The name of the WorkflowEdge to delete.

    try:
        # DeleteWorkflowEdge deletes a WorkflowEdge. If the WorkflowEdge does not exist an error is returned
        api_response = api_instance.workflow_edge_service_delete_workflow_edge(name_7)
        print("The response of WorkflowEdgeServiceApi->workflow_edge_service_delete_workflow_edge:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowEdgeServiceApi->workflow_edge_service_delete_workflow_edge: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name_7** | **str**| Required. The name of the WorkflowEdge to delete. | 

### Return type

[**V1DeleteWorkflowEdgeResponse**](V1DeleteWorkflowEdgeResponse.md)

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

