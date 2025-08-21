# V1PromptLibraryItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] [readonly] 
**create_time** | **datetime** | Output only. Timestamp when the item was created. | [optional] [readonly] 
**creator** | **str** | Output only. Name of the user or service that requested creation of the item. | [optional] [readonly] 
**update_time** | **datetime** | Output only. Optional. Timestamp when the item was last updated. | [optional] [readonly] 
**updater** | **str** | Output only. Optional. Name of the user or service that requested update of the item. | [optional] [readonly] 
**delete_time** | **datetime** | Output only. Optional. Set when the item is deleted. When set, item should be considered as deleted. | [optional] [readonly] 
**deleter** | **str** | Output only. Optional. Name of the user or service that requested deletion of the item. | [optional] [readonly] 
**display_name** | **str** | Human readable name of the item. | [optional] 
**description** | **str** | Optional. Arbitrary description of the item. | [optional] 
**test_suite_url** | **str** | URL of the test suite which is represented by this library item. | [optional] 
**test_count** | **int** | Number of tests in the test suite. | [optional] 
**test_case_count** | **int** | Number of test cases in the test suite. | [optional] 
**evaluates** | [**List[V1TestSuiteEvaluates]**](V1TestSuiteEvaluates.md) | Types of systems evaluated by this item - like RAG (has corpus), LLM (no corpus) or agents. | [optional] 
**categories** | **List[str]** | Categories of test cases in the item - like question_answering or summarization. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_prompt_library_item import V1PromptLibraryItem

# TODO update the JSON string below
json = "{}"
# create an instance of V1PromptLibraryItem from a JSON string
v1_prompt_library_item_instance = V1PromptLibraryItem.from_json(json)
# print the JSON string representation of the object
print(V1PromptLibraryItem.to_json())

# convert the object into a dict
v1_prompt_library_item_dict = v1_prompt_library_item_instance.to_dict()
# create an instance of V1PromptLibraryItem from a dict
v1_prompt_library_item_from_dict = V1PromptLibraryItem.from_dict(v1_prompt_library_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


