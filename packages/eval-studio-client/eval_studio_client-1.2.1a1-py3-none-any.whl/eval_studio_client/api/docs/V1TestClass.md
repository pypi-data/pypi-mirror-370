# V1TestClass


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] [readonly] 
**create_time** | **datetime** | Output only. Timestamp when the TestClass was created. | [optional] [readonly] 
**creator** | **str** | Output only. Name of the user or service that requested creation of the TestClass. | [optional] [readonly] 
**update_time** | **datetime** | Output only. Optional. Timestamp when the TestClass was last updated. | [optional] [readonly] 
**updater** | **str** | Output only. Optional. Name of the user or service that requested update of the TestClass. | [optional] [readonly] 
**delete_time** | **datetime** | Output only. Optional. Set when the TestClass is deleted. When set, TestClass should be considered as deleted. | [optional] [readonly] 
**deleter** | **str** | Output only. Optional. Name of the user or service that requested deletion of the TestClass. | [optional] [readonly] 
**display_name** | **str** | Human readable name of the TestClass. | [optional] 
**description** | **str** | Optional. Arbitrary description of the TestClass. | [optional] 
**evaluators** | **List[str]** | List of evaluators that are part of the TestClass. | [optional] 
**recommended_tests** | **List[str]** | List of recommended Tests that are part of the TestClass. | [optional] 
**test_class_type** | [**V1TestClassType**](V1TestClassType.md) |  | [optional] 
**tags** | **List[str]** | List of tags. Can contain any string, some examples are \&quot;SR 11-7\&quot;, \&quot;NIST\&quot;, etc. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_test_class import V1TestClass

# TODO update the JSON string below
json = "{}"
# create an instance of V1TestClass from a JSON string
v1_test_class_instance = V1TestClass.from_json(json)
# print the JSON string representation of the object
print(V1TestClass.to_json())

# convert the object into a dict
v1_test_class_dict = v1_test_class_instance.to_dict()
# create an instance of V1TestClass from a dict
v1_test_class_from_dict = V1TestClass.from_dict(v1_test_class_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


