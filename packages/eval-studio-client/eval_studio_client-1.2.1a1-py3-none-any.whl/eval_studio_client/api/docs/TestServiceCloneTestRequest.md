# TestServiceCloneTestRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**new_test_display_name** | **str** | Optional. Name of the newly created test. | [optional] 
**new_test_description** | **str** | Optional. Description of the newly created Test. | [optional] 

## Example

```python
from eval_studio_client.api.models.test_service_clone_test_request import TestServiceCloneTestRequest

# TODO update the JSON string below
json = "{}"
# create an instance of TestServiceCloneTestRequest from a JSON string
test_service_clone_test_request_instance = TestServiceCloneTestRequest.from_json(json)
# print the JSON string representation of the object
print(TestServiceCloneTestRequest.to_json())

# convert the object into a dict
test_service_clone_test_request_dict = test_service_clone_test_request_instance.to_dict()
# create an instance of TestServiceCloneTestRequest from a dict
test_service_clone_test_request_from_dict = TestServiceCloneTestRequest.from_dict(test_service_clone_test_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


