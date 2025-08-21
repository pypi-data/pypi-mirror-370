# V1Perturbator


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] [readonly] 
**create_time** | **datetime** | Output only. Timestamp when the Perturbator was created. | [optional] [readonly] 
**creator** | **str** | Output only. Name of the user or service that requested creation of the Perturbator. | [optional] [readonly] 
**update_time** | **datetime** | Output only. Optional. Timestamp when the Perturbator was last updated. | [optional] [readonly] 
**updater** | **str** | Output only. Optional. Name of the user or service that requested update of the Perturbator. | [optional] [readonly] 
**delete_time** | **datetime** | Output only. Optional. Set when the Perturbator is deleted. When set Perturbator should be considered as deleted. | [optional] [readonly] 
**deleter** | **str** | Output only. Optional. Name of the user or service that requested deletion of the Perturbator. | [optional] [readonly] 
**display_name** | **str** | Human readable name of the Perturbator. | [optional] 
**description** | **str** | Optional. Arbitrary description of the Perturbator. | [optional] 
**identifier** | **str** | Well known identifier of the Perturbator implementation. | [optional] 
**tags** | **List[str]** | Optional. Tags or other identifiers of the Perturbator. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_perturbator import V1Perturbator

# TODO update the JSON string below
json = "{}"
# create an instance of V1Perturbator from a JSON string
v1_perturbator_instance = V1Perturbator.from_json(json)
# print the JSON string representation of the object
print(V1Perturbator.to_json())

# convert the object into a dict
v1_perturbator_dict = v1_perturbator_instance.to_dict()
# create an instance of V1Perturbator from a dict
v1_perturbator_from_dict = V1Perturbator.from_dict(v1_perturbator_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


