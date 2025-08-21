# V1Evaluator


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] [readonly] 
**create_time** | **datetime** | Output only. Timestamp when the Evaluator was created. | [optional] [readonly] 
**creator** | **str** | Output only. Name of the user or service that requested creation of the Evaluator. | [optional] [readonly] 
**update_time** | **datetime** | Output only. Optional. Timestamp when the Evaluator was last updated. | [optional] [readonly] 
**updater** | **str** | Output only. Optional. Name of the user or service that requested update of the Evaluator. | [optional] [readonly] 
**delete_time** | **datetime** | Output only. Optional. Set when the Evaluator is deleted. When set Evaluator should be considered as deleted. | [optional] [readonly] 
**deleter** | **str** | Output only. Optional. Name of the user or service that requested deletion of the Evaluator. | [optional] [readonly] 
**display_name** | **str** | Human readable name of the Evaluator. | [optional] 
**description** | **str** | Optional. Arbitrary description of the Evaluator. | [optional] 
**content** | **bytearray** | Base64 encoded Evaluator implementation. | [optional] 
**mime_type** | **str** | MIME type of the Evaluator implementation, e.g.: \&quot;text/x-python\&quot; or \&quot;application/zip\&quot;. | [optional] 
**filename** | **str** | Filename of the Evaluator implementation, e.g.: \&quot;evaluator.py\&quot; or \&quot;evaluator.zip\&quot;. | [optional] 
**identifier** | **str** | Well known identifier of the Evaluator implementation. | [optional] 
**tags** | **List[str]** | Optional. Tags or other identifiers of the Evaluator. | [optional] 
**parameters** | [**List[V1EvaluatorParameter]**](V1EvaluatorParameter.md) | Optional. Additional parameters of the Evaluator. | [optional] 
**brief_description** | **str** | Optional. Short preview of the Evaluator&#39;s description. | [optional] 
**enabled** | **bool** | Output only. Whether this Evaluator can be used for creating evaluations. Evaluator might be disabled because it has some external requirements that are not met. | [optional] [readonly] 
**tagline** | **str** | Output only. Tagline is a short (single-line) and high-level description of the evaluator. | [optional] [readonly] 
**primary_metric** | **str** | Output only. Optional. The name of the primary metric. | [optional] [readonly] 
**primary_metric_default_threshold** | **float** | Output only. Optional. Default threshold of the primary metric. Value must be ignored if primary_metric is invalid. | [optional] [readonly] 

## Example

```python
from eval_studio_client.api.models.v1_evaluator import V1Evaluator

# TODO update the JSON string below
json = "{}"
# create an instance of V1Evaluator from a JSON string
v1_evaluator_instance = V1Evaluator.from_json(json)
# print the JSON string representation of the object
print(V1Evaluator.to_json())

# convert the object into a dict
v1_evaluator_dict = v1_evaluator_instance.to_dict()
# create an instance of V1Evaluator from a dict
v1_evaluator_from_dict = V1Evaluator.from_dict(v1_evaluator_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


