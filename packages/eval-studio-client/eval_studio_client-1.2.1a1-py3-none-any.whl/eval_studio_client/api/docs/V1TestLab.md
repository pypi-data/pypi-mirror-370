# V1TestLab


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] [readonly] 
**create_time** | **datetime** | Output only. Timestamp when the Test was created. | [optional] [readonly] 
**creator** | **str** | Output only. Name of the user or service that requested creation of the TestCase. | [optional] [readonly] 
**update_time** | **datetime** | Output only. Optional. Timestamp when the TestCase was last updated. | [optional] [readonly] 
**updater** | **str** | Output only. Optional. Name of the user or service that requested update of the TestCase. | [optional] [readonly] 
**delete_time** | **datetime** | Output only. Optional. Set when the TestCase is deleted. When set TestCase should be considered as deleted. | [optional] [readonly] 
**deleter** | **str** | Output only. Optional. Name of the user or service that requested deletion of the TestCase. | [optional] [readonly] 
**model** | **str** | Immutable. Model used in this test lab. | [optional] 
**test_cases** | **List[str]** | Immutable. Test cases used in this test lab. | [optional] 
**content** | **bytearray** | Immutable. Raw content of the Test Lab. | [optional] 
**llm_models** | **List[str]** | Immutable. List of LLM models used. | [optional] 
**model_parameters** | **str** | Immutable. Optional. Parameters overrides in JSON format. | [optional] 
**h2ogpte_collection** | **str** | The existing collection name in H2OGPTe. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_test_lab import V1TestLab

# TODO update the JSON string below
json = "{}"
# create an instance of V1TestLab from a JSON string
v1_test_lab_instance = V1TestLab.from_json(json)
# print the JSON string representation of the object
print(V1TestLab.to_json())

# convert the object into a dict
v1_test_lab_dict = v1_test_lab_instance.to_dict()
# create an instance of V1TestLab from a dict
v1_test_lab_from_dict = V1TestLab.from_dict(v1_test_lab_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


