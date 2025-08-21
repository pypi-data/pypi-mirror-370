# TestServiceImportTestCasesFromLibraryRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**operation** | **str** | Required. The Operation processing this prompt library retrieval process. | [optional] 
**test_suite_url** | **str** | Required. The URL of the library test suite to get TestCases from (sample). | [optional] 
**count** | **int** | Required. The number of TestCases to get from the library. | [optional] 
**test_document_urls** | **List[str]** | Optional. The list of target Test corpus document URLs to skip when returning library TestCases corpus. | [optional] 

## Example

```python
from eval_studio_client.api.models.test_service_import_test_cases_from_library_request import TestServiceImportTestCasesFromLibraryRequest

# TODO update the JSON string below
json = "{}"
# create an instance of TestServiceImportTestCasesFromLibraryRequest from a JSON string
test_service_import_test_cases_from_library_request_instance = TestServiceImportTestCasesFromLibraryRequest.from_json(json)
# print the JSON string representation of the object
print(TestServiceImportTestCasesFromLibraryRequest.to_json())

# convert the object into a dict
test_service_import_test_cases_from_library_request_dict = test_service_import_test_cases_from_library_request_instance.to_dict()
# create an instance of TestServiceImportTestCasesFromLibraryRequest from a dict
test_service_import_test_cases_from_library_request_from_dict = TestServiceImportTestCasesFromLibraryRequest.from_dict(test_service_import_test_cases_from_library_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


