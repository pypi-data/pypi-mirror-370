# eval_studio_client.api.WhoAmIServiceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**who_am_i_service_who_am_i**](WhoAmIServiceApi.md#who_am_i_service_who_am_i) | **GET** /v1/whoAmI | WhoAmI is used to retrieve the caller&#39;s identity.


# **who_am_i_service_who_am_i**
> V1WhoAmIResponse who_am_i_service_who_am_i()

WhoAmI is used to retrieve the caller's identity.

### Example


```python
import eval_studio_client.api
from eval_studio_client.api.models.v1_who_am_i_response import V1WhoAmIResponse
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
    api_instance = eval_studio_client.api.WhoAmIServiceApi(api_client)

    try:
        # WhoAmI is used to retrieve the caller's identity.
        api_response = api_instance.who_am_i_service_who_am_i()
        print("The response of WhoAmIServiceApi->who_am_i_service_who_am_i:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WhoAmIServiceApi->who_am_i_service_who_am_i: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**V1WhoAmIResponse**](V1WhoAmIResponse.md)

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

