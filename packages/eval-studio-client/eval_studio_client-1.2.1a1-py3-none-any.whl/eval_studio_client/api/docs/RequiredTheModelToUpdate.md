# RequiredTheModelToUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**create_time** | **datetime** | Output only. Timestamp when the Model was created. | [optional] [readonly] 
**creator** | **str** | Output only. Name of the user or service that requested creation of the Model. | [optional] [readonly] 
**update_time** | **datetime** | Output only. Optional. Timestamp when the Model was last updated. | [optional] [readonly] 
**updater** | **str** | Output only. Optional. Name of the user or service that requested update of the Model. | [optional] [readonly] 
**delete_time** | **datetime** | Output only. Optional. Set when the Model is deleted. When set Model should be considered as deleted. | [optional] [readonly] 
**deleter** | **str** | Output only. Optional. Name of the user or service that requested deletion of the Model. | [optional] [readonly] 
**display_name** | **str** | Human readable name of the Model. | [optional] 
**description** | **str** | Optional. Arbitrary description of the Model. | [optional] 
**url** | **str** | Optional. Immutable. Absolute URL to the Model. | [optional] 
**api_key** | **str** | Optional. API key used to access the Model. Not set for read calls (i.e. get, list) by public clients (front-end). Set only for internal (server-to-worker) communication. | [optional] 
**type** | [**V1ModelType**](V1ModelType.md) |  | [optional] 
**parameters** | **str** | Optional. Model specific parameters in JSON format. | [optional] 
**demo** | **bool** | Output only. Whether the Model is a demo resource or not. Demo resources are read only. | [optional] [readonly] 

## Example

```python
from eval_studio_client.api.models.required_the_model_to_update import RequiredTheModelToUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of RequiredTheModelToUpdate from a JSON string
required_the_model_to_update_instance = RequiredTheModelToUpdate.from_json(json)
# print the JSON string representation of the object
print(RequiredTheModelToUpdate.to_json())

# convert the object into a dict
required_the_model_to_update_dict = required_the_model_to_update_instance.to_dict()
# create an instance of RequiredTheModelToUpdate from a dict
required_the_model_to_update_from_dict = RequiredTheModelToUpdate.from_dict(required_the_model_to_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


