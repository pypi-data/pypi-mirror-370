# eval_studio_client.api.PerturbationServiceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**perturbation_service_create_perturbation**](PerturbationServiceApi.md#perturbation_service_create_perturbation) | **POST** /v1/{parent}/perturbations | 


# **perturbation_service_create_perturbation**
> V1CreatePerturbationResponse perturbation_service_create_perturbation(parent, body)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.perturbation_service_create_perturbation_request import PerturbationServiceCreatePerturbationRequest
from eval_studio_client.api.models.v1_create_perturbation_response import V1CreatePerturbationResponse
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
    api_instance = eval_studio_client.api.PerturbationServiceApi(api_client)
    parent = 'parent_example' # str | Required. The Test being perturbed.
    body = eval_studio_client.api.PerturbationServiceCreatePerturbationRequest() # PerturbationServiceCreatePerturbationRequest | 

    try:
        api_response = api_instance.perturbation_service_create_perturbation(parent, body)
        print("The response of PerturbationServiceApi->perturbation_service_create_perturbation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PerturbationServiceApi->perturbation_service_create_perturbation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **parent** | **str**| Required. The Test being perturbed. | 
 **body** | [**PerturbationServiceCreatePerturbationRequest**](PerturbationServiceCreatePerturbationRequest.md)|  | 

### Return type

[**V1CreatePerturbationResponse**](V1CreatePerturbationResponse.md)

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

