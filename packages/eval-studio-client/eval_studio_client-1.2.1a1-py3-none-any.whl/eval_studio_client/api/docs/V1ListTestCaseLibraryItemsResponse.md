# V1ListTestCaseLibraryItemsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**prompt_library_items** | [**List[V1PromptLibraryItem]**](V1PromptLibraryItem.md) | Test suites library items. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_list_test_case_library_items_response import V1ListTestCaseLibraryItemsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListTestCaseLibraryItemsResponse from a JSON string
v1_list_test_case_library_items_response_instance = V1ListTestCaseLibraryItemsResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListTestCaseLibraryItemsResponse.to_json())

# convert the object into a dict
v1_list_test_case_library_items_response_dict = v1_list_test_case_library_items_response_instance.to_dict()
# create an instance of V1ListTestCaseLibraryItemsResponse from a dict
v1_list_test_case_library_items_response_from_dict = V1ListTestCaseLibraryItemsResponse.from_dict(v1_list_test_case_library_items_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


