# V1ProblemAndAction


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** | Output only. Problem description. | [optional] [readonly] 
**severity** | **str** | Output only. Problem severity. | [optional] [readonly] 
**problem_type** | **str** | Output only. Problem type. | [optional] [readonly] 
**problem_attrs** | **Dict[str, str]** | Output only. Problem attributes. | [optional] [readonly] 
**actions_description** | **str** | Output only. Description of actions to mitigate the problem. | [optional] [readonly] 
**explainer_id** | **str** | Output only. ID of the explainer which identified the problem. | [optional] [readonly] 
**explainer_name** | **str** | Output only. Display name of the explainer which identified the problem. | [optional] [readonly] 
**explanation_type** | **str** | Output only. Type of the explanation which can clarify the problem. | [optional] [readonly] 
**explanation_name** | **str** | Output only. Name of the explanation which can clarify the problem. | [optional] [readonly] 
**explanation_mime** | **str** | Output only. Media type of the explanation which can clarify the problem. | [optional] [readonly] 
**resources** | **List[str]** | Output only. Problem resources. | [optional] [readonly] 

## Example

```python
from eval_studio_client.api.models.v1_problem_and_action import V1ProblemAndAction

# TODO update the JSON string below
json = "{}"
# create an instance of V1ProblemAndAction from a JSON string
v1_problem_and_action_instance = V1ProblemAndAction.from_json(json)
# print the JSON string representation of the object
print(V1ProblemAndAction.to_json())

# convert the object into a dict
v1_problem_and_action_dict = v1_problem_and_action_instance.to_dict()
# create an instance of V1ProblemAndAction from a dict
v1_problem_and_action_from_dict = V1ProblemAndAction.from_dict(v1_problem_and_action_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


