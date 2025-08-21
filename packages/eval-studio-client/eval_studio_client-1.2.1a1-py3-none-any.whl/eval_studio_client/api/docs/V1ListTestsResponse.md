# V1ListTestsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tests** | [**List[V1Test]**](V1Test.md) | The Tests that match the request. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_list_tests_response import V1ListTestsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListTestsResponse from a JSON string
v1_list_tests_response_instance = V1ListTestsResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListTestsResponse.to_json())

# convert the object into a dict
v1_list_tests_response_dict = v1_list_tests_response_instance.to_dict()
# create an instance of V1ListTestsResponse from a dict
v1_list_tests_response_from_dict = V1ListTestsResponse.from_dict(v1_list_tests_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


