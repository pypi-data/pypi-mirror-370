# eval_studio_client.api.AdversarialInputsServiceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**adversarial_inputs_service_test_adversarial_inputs_robustness**](AdversarialInputsServiceApi.md#adversarial_inputs_service_test_adversarial_inputs_robustness) | **POST** /v1/{test}:testAdversarialInputsRobustness | 


# **adversarial_inputs_service_test_adversarial_inputs_robustness**
> V1Operation adversarial_inputs_service_test_adversarial_inputs_robustness(test, body)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.adversarial_inputs_service_test_adversarial_inputs_robustness_request import AdversarialInputsServiceTestAdversarialInputsRobustnessRequest
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
    api_instance = eval_studio_client.api.AdversarialInputsServiceApi(api_client)
    test = 'test_example' # str | Required. The Test to which the adversarial inputs TestCases will be added.
    body = eval_studio_client.api.AdversarialInputsServiceTestAdversarialInputsRobustnessRequest() # AdversarialInputsServiceTestAdversarialInputsRobustnessRequest | 

    try:
        api_response = api_instance.adversarial_inputs_service_test_adversarial_inputs_robustness(test, body)
        print("The response of AdversarialInputsServiceApi->adversarial_inputs_service_test_adversarial_inputs_robustness:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdversarialInputsServiceApi->adversarial_inputs_service_test_adversarial_inputs_robustness: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test** | **str**| Required. The Test to which the adversarial inputs TestCases will be added. | 
 **body** | [**AdversarialInputsServiceTestAdversarialInputsRobustnessRequest**](AdversarialInputsServiceTestAdversarialInputsRobustnessRequest.md)|  | 

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

