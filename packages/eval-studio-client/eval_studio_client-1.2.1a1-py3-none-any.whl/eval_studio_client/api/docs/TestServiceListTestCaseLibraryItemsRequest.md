# TestServiceListTestCaseLibraryItemsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**filter_by_categories** | **List[str]** | Optional. Filter by categories. | [optional] 
**filter_by_purposes** | **List[str]** | Optional. Filter by purposes. | [optional] 
**filter_by_evaluates** | **List[str]** | Optional. Filter by evaluates. | [optional] 
**filter_by_origin** | **str** | Optional. Filter by origin. | [optional] 
**filter_by_test_case_count** | **int** | Optional. Filter by test case count. | [optional] 
**filter_by_test_count** | **int** | Optional. Filter by test count. | [optional] 
**filter_by_fts** | **str** | Optional. Filter by FTS. | [optional] 

## Example

```python
from eval_studio_client.api.models.test_service_list_test_case_library_items_request import TestServiceListTestCaseLibraryItemsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of TestServiceListTestCaseLibraryItemsRequest from a JSON string
test_service_list_test_case_library_items_request_instance = TestServiceListTestCaseLibraryItemsRequest.from_json(json)
# print the JSON string representation of the object
print(TestServiceListTestCaseLibraryItemsRequest.to_json())

# convert the object into a dict
test_service_list_test_case_library_items_request_dict = test_service_list_test_case_library_items_request_instance.to_dict()
# create an instance of TestServiceListTestCaseLibraryItemsRequest from a dict
test_service_list_test_case_library_items_request_from_dict = TestServiceListTestCaseLibraryItemsRequest.from_dict(test_service_list_test_case_library_items_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


