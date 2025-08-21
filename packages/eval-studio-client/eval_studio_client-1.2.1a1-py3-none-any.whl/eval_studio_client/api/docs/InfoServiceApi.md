# eval_studio_client.api.InfoServiceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**info_service_get_info**](InfoServiceApi.md#info_service_get_info) | **GET** /v1/info | 
[**info_service_get_stats**](InfoServiceApi.md#info_service_get_stats) | **GET** /v1/stats | 


# **info_service_get_info**
> V1GetInfoResponse info_service_get_info()



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_get_info_response import V1GetInfoResponse
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
    api_instance = eval_studio_client.api.InfoServiceApi(api_client)

    try:
        api_response = api_instance.info_service_get_info()
        print("The response of InfoServiceApi->info_service_get_info:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling InfoServiceApi->info_service_get_info: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**V1GetInfoResponse**](V1GetInfoResponse.md)

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

# **info_service_get_stats**
> V1GetStatsResponse info_service_get_stats()



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_get_stats_response import V1GetStatsResponse
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
    api_instance = eval_studio_client.api.InfoServiceApi(api_client)

    try:
        api_response = api_instance.info_service_get_stats()
        print("The response of InfoServiceApi->info_service_get_stats:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling InfoServiceApi->info_service_get_stats: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**V1GetStatsResponse**](V1GetStatsResponse.md)

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

