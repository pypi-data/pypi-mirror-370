# eval_studio_client.api.HumanCalibrationServiceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**human_calibration_service_estimate_threshold**](HumanCalibrationServiceApi.md#human_calibration_service_estimate_threshold) | **POST** /v1:estimateThreshold | EstimateThreshold runs a threshold estimation process based on human labeling of randomly sampled test-cases.


# **human_calibration_service_estimate_threshold**
> V1Operation human_calibration_service_estimate_threshold(body)

EstimateThreshold runs a threshold estimation process based on human labeling of randomly sampled test-cases.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_estimate_threshold_request import V1EstimateThresholdRequest
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
    api_instance = eval_studio_client.api.HumanCalibrationServiceApi(api_client)
    body = eval_studio_client.api.V1EstimateThresholdRequest() # V1EstimateThresholdRequest | 

    try:
        # EstimateThreshold runs a threshold estimation process based on human labeling of randomly sampled test-cases.
        api_response = api_instance.human_calibration_service_estimate_threshold(body)
        print("The response of HumanCalibrationServiceApi->human_calibration_service_estimate_threshold:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling HumanCalibrationServiceApi->human_calibration_service_estimate_threshold: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**V1EstimateThresholdRequest**](V1EstimateThresholdRequest.md)|  | 

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

