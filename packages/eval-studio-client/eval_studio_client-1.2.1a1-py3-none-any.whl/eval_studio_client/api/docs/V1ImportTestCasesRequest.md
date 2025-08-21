# V1ImportTestCasesRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**test** | **str** | Required. The Test for which to get TestCases. | [optional] 
**operation** | **str** | Required. The Operation processing this prompt library retrieval process. | [optional] 
**test_suite_url** | **str** | Required. The URL of the library test suite to get TestCases from (sample). | [optional] 
**count** | **int** | Required. The number of TestCases to get from the library. | [optional] 
**test_document_urls** | **List[str]** | Optional. The list of target Test corpus document URLs which don&#39;t have to be included when returning library TestCases corpus as they are already in the Test. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_import_test_cases_request import V1ImportTestCasesRequest

# TODO update the JSON string below
json = "{}"
# create an instance of V1ImportTestCasesRequest from a JSON string
v1_import_test_cases_request_instance = V1ImportTestCasesRequest.from_json(json)
# print the JSON string representation of the object
print(V1ImportTestCasesRequest.to_json())

# convert the object into a dict
v1_import_test_cases_request_dict = v1_import_test_cases_request_instance.to_dict()
# create an instance of V1ImportTestCasesRequest from a dict
v1_import_test_cases_request_from_dict = V1ImportTestCasesRequest.from_dict(v1_import_test_cases_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


