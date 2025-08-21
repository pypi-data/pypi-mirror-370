# TestServiceGrantTestAccessRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**subject** | **str** | Required. The subject to grant access to. | [optional] 
**role** | [**V1Role**](V1Role.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.test_service_grant_test_access_request import TestServiceGrantTestAccessRequest

# TODO update the JSON string below
json = "{}"
# create an instance of TestServiceGrantTestAccessRequest from a JSON string
test_service_grant_test_access_request_instance = TestServiceGrantTestAccessRequest.from_json(json)
# print the JSON string representation of the object
print(TestServiceGrantTestAccessRequest.to_json())

# convert the object into a dict
test_service_grant_test_access_request_dict = test_service_grant_test_access_request_instance.to_dict()
# create an instance of TestServiceGrantTestAccessRequest from a dict
test_service_grant_test_access_request_from_dict = TestServiceGrantTestAccessRequest.from_dict(test_service_grant_test_access_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


