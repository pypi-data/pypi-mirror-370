# V1FindAllTestCasesByIDResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**test_cases** | [**List[V1TestCase]**](V1TestCase.md) | The list of TestCases. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_find_all_test_cases_by_id_response import V1FindAllTestCasesByIDResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1FindAllTestCasesByIDResponse from a JSON string
v1_find_all_test_cases_by_id_response_instance = V1FindAllTestCasesByIDResponse.from_json(json)
# print the JSON string representation of the object
print(V1FindAllTestCasesByIDResponse.to_json())

# convert the object into a dict
v1_find_all_test_cases_by_id_response_dict = v1_find_all_test_cases_by_id_response_instance.to_dict()
# create an instance of V1FindAllTestCasesByIDResponse from a dict
v1_find_all_test_cases_by_id_response_from_dict = V1FindAllTestCasesByIDResponse.from_dict(v1_find_all_test_cases_by_id_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


