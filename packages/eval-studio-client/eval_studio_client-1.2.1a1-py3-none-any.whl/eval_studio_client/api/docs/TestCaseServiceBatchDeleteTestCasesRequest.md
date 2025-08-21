# TestCaseServiceBatchDeleteTestCasesRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**names** | **List[str]** | The list of TestCase IDs to delete. | [optional] 

## Example

```python
from eval_studio_client.api.models.test_case_service_batch_delete_test_cases_request import TestCaseServiceBatchDeleteTestCasesRequest

# TODO update the JSON string below
json = "{}"
# create an instance of TestCaseServiceBatchDeleteTestCasesRequest from a JSON string
test_case_service_batch_delete_test_cases_request_instance = TestCaseServiceBatchDeleteTestCasesRequest.from_json(json)
# print the JSON string representation of the object
print(TestCaseServiceBatchDeleteTestCasesRequest.to_json())

# convert the object into a dict
test_case_service_batch_delete_test_cases_request_dict = test_case_service_batch_delete_test_cases_request_instance.to_dict()
# create an instance of TestCaseServiceBatchDeleteTestCasesRequest from a dict
test_case_service_batch_delete_test_cases_request_from_dict = TestCaseServiceBatchDeleteTestCasesRequest.from_dict(test_case_service_batch_delete_test_cases_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


