# V1ListTestCasesResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**test_cases** | [**List[V1TestCase]**](V1TestCase.md) | The list of TestCases. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_list_test_cases_response import V1ListTestCasesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListTestCasesResponse from a JSON string
v1_list_test_cases_response_instance = V1ListTestCasesResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListTestCasesResponse.to_json())

# convert the object into a dict
v1_list_test_cases_response_dict = v1_list_test_cases_response_instance.to_dict()
# create an instance of V1ListTestCasesResponse from a dict
v1_list_test_cases_response_from_dict = V1ListTestCasesResponse.from_dict(v1_list_test_cases_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


