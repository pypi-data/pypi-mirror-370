# V1ListPromptLibraryItemsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**prompt_library_items** | [**List[V1PromptLibraryItem]**](V1PromptLibraryItem.md) | Prompt library items (test suites). | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_list_prompt_library_items_response import V1ListPromptLibraryItemsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListPromptLibraryItemsResponse from a JSON string
v1_list_prompt_library_items_response_instance = V1ListPromptLibraryItemsResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListPromptLibraryItemsResponse.to_json())

# convert the object into a dict
v1_list_prompt_library_items_response_dict = v1_list_prompt_library_items_response_instance.to_dict()
# create an instance of V1ListPromptLibraryItemsResponse from a dict
v1_list_prompt_library_items_response_from_dict = V1ListPromptLibraryItemsResponse.from_dict(v1_list_prompt_library_items_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


