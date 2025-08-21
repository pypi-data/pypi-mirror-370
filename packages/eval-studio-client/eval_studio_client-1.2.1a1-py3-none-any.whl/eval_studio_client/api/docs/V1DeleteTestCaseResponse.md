# V1DeleteTestCaseResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**test_case** | [**V1TestCase**](V1TestCase.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_delete_test_case_response import V1DeleteTestCaseResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1DeleteTestCaseResponse from a JSON string
v1_delete_test_case_response_instance = V1DeleteTestCaseResponse.from_json(json)
# print the JSON string representation of the object
print(V1DeleteTestCaseResponse.to_json())

# convert the object into a dict
v1_delete_test_case_response_dict = v1_delete_test_case_response_instance.to_dict()
# create an instance of V1DeleteTestCaseResponse from a dict
v1_delete_test_case_response_from_dict = V1DeleteTestCaseResponse.from_dict(v1_delete_test_case_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


