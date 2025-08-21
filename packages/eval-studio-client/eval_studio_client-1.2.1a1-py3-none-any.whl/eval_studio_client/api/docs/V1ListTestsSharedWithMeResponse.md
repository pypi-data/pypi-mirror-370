# V1ListTestsSharedWithMeResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tests** | [**List[V1Test]**](V1Test.md) | The Tests that match the request. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_list_tests_shared_with_me_response import V1ListTestsSharedWithMeResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListTestsSharedWithMeResponse from a JSON string
v1_list_tests_shared_with_me_response_instance = V1ListTestsSharedWithMeResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListTestsSharedWithMeResponse.to_json())

# convert the object into a dict
v1_list_tests_shared_with_me_response_dict = v1_list_tests_shared_with_me_response_instance.to_dict()
# create an instance of V1ListTestsSharedWithMeResponse from a dict
v1_list_tests_shared_with_me_response_from_dict = V1ListTestsSharedWithMeResponse.from_dict(v1_list_tests_shared_with_me_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


