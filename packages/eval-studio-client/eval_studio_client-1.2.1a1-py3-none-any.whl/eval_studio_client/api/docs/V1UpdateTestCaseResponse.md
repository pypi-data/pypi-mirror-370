# V1UpdateTestCaseResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**test_case** | [**V1TestCase**](V1TestCase.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_update_test_case_response import V1UpdateTestCaseResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1UpdateTestCaseResponse from a JSON string
v1_update_test_case_response_instance = V1UpdateTestCaseResponse.from_json(json)
# print the JSON string representation of the object
print(V1UpdateTestCaseResponse.to_json())

# convert the object into a dict
v1_update_test_case_response_dict = v1_update_test_case_response_instance.to_dict()
# create an instance of V1UpdateTestCaseResponse from a dict
v1_update_test_case_response_from_dict = V1UpdateTestCaseResponse.from_dict(v1_update_test_case_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


