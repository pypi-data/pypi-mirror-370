# V1Insight

Insight represents additional information about the evaluation.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** | Description of the insight. | [optional] 
**actions_description** | **str** | Description of the actions that can be taken based on the insight. | [optional] 
**actions_codes** | **List[str]** | List of codes that can be used to take actions based on the insight. | [optional] 
**evaluator_id** | **str** |  | [optional] 
**evaluator_display_name** | **str** | Human readable name of the evaluator that generated the insight, e.g. Tokens presence. | [optional] 
**explanation_type** | **str** | Type of the explanation. | [optional] 
**explanation_name** | **str** | Name of the explanation. | [optional] 
**explanation_mime** | **str** | MIME type of the explanation. | [optional] 
**resources** | **List[str]** | List of resources that can be used to take actions based on the insight. | [optional] 
**insight_type** | **str** | Type of the insight. | [optional] 
**insight_attrs** | **Dict[str, str]** | Attributes of the insight. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_insight import V1Insight

# TODO update the JSON string below
json = "{}"
# create an instance of V1Insight from a JSON string
v1_insight_instance = V1Insight.from_json(json)
# print the JSON string representation of the object
print(V1Insight.to_json())

# convert the object into a dict
v1_insight_dict = v1_insight_instance.to_dict()
# create an instance of V1Insight from a dict
v1_insight_from_dict = V1Insight.from_dict(v1_insight_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


