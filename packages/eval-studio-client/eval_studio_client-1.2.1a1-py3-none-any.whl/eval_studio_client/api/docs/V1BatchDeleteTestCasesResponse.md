# V1BatchDeleteTestCasesResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**test_cases** | [**List[V1TestCase]**](V1TestCase.md) | The list of deleted TestCases. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_batch_delete_test_cases_response import V1BatchDeleteTestCasesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1BatchDeleteTestCasesResponse from a JSON string
v1_batch_delete_test_cases_response_instance = V1BatchDeleteTestCasesResponse.from_json(json)
# print the JSON string representation of the object
print(V1BatchDeleteTestCasesResponse.to_json())

# convert the object into a dict
v1_batch_delete_test_cases_response_dict = v1_batch_delete_test_cases_response_instance.to_dict()
# create an instance of V1BatchDeleteTestCasesResponse from a dict
v1_batch_delete_test_cases_response_from_dict = V1BatchDeleteTestCasesResponse.from_dict(v1_batch_delete_test_cases_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


