# TestServiceRevokeTestAccessRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**subject** | **str** | Required. The subject to revoke access to. | [optional] 
**role** | [**V1Role**](V1Role.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.test_service_revoke_test_access_request import TestServiceRevokeTestAccessRequest

# TODO update the JSON string below
json = "{}"
# create an instance of TestServiceRevokeTestAccessRequest from a JSON string
test_service_revoke_test_access_request_instance = TestServiceRevokeTestAccessRequest.from_json(json)
# print the JSON string representation of the object
print(TestServiceRevokeTestAccessRequest.to_json())

# convert the object into a dict
test_service_revoke_test_access_request_dict = test_service_revoke_test_access_request_instance.to_dict()
# create an instance of TestServiceRevokeTestAccessRequest from a dict
test_service_revoke_test_access_request_from_dict = TestServiceRevokeTestAccessRequest.from_dict(test_service_revoke_test_access_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


