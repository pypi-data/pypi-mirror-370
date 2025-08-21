# eval_studio_client.api.LeaderboardReportServiceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**leaderboard_report_service_get_leaderboard_report**](LeaderboardReportServiceApi.md#leaderboard_report_service_get_leaderboard_report) | **GET** /v1/{name_3} | 


# **leaderboard_report_service_get_leaderboard_report**
> V1GetLeaderboardReportResponse leaderboard_report_service_get_leaderboard_report(name_3)



### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_get_leaderboard_report_response import V1GetLeaderboardReportResponse
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
    api_instance = eval_studio_client.api.LeaderboardReportServiceApi(api_client)
    name_3 = 'name_3_example' # str | Required. The name of the Leaderboard to retrieve.

    try:
        api_response = api_instance.leaderboard_report_service_get_leaderboard_report(name_3)
        print("The response of LeaderboardReportServiceApi->leaderboard_report_service_get_leaderboard_report:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LeaderboardReportServiceApi->leaderboard_report_service_get_leaderboard_report: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name_3** | **str**| Required. The name of the Leaderboard to retrieve. | 

### Return type

[**V1GetLeaderboardReportResponse**](V1GetLeaderboardReportResponse.md)

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

