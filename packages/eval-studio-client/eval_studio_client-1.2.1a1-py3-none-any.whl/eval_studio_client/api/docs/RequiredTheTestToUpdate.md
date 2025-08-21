# RequiredTheTestToUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**create_time** | **datetime** | Output only. Timestamp when the Test was created. | [optional] [readonly] 
**creator** | **str** | Output only. Name of the user or service that requested creation of the Test. | [optional] [readonly] 
**update_time** | **datetime** | Output only. Optional. Timestamp when the Test was last updated. | [optional] [readonly] 
**updater** | **str** | Output only. Optional. Name of the user or service that requested update of the Test. | [optional] [readonly] 
**delete_time** | **datetime** | Output only. Optional. Set when the Test is deleted. When set, Test should be considered as deleted. | [optional] [readonly] 
**deleter** | **str** | Output only. Optional. Name of the user or service that requested deletion of the Test. | [optional] [readonly] 
**display_name** | **str** | Human readable name of the Test. | [optional] 
**description** | **str** | Optional. Arbitrary description of the Test. | [optional] 
**documents** | **List[str]** | Immutable. Resource names of Documents assigned to the Test. | [optional] 
**tags** | **List[str]** | Tags assigned to the Test. | [optional] 
**demo** | **bool** | Output only. Whether the Test is a demo resource or not. Demo resources are read only. | [optional] [readonly] 
**type** | [**V1TestType**](V1TestType.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.required_the_test_to_update import RequiredTheTestToUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of RequiredTheTestToUpdate from a JSON string
required_the_test_to_update_instance = RequiredTheTestToUpdate.from_json(json)
# print the JSON string representation of the object
print(RequiredTheTestToUpdate.to_json())

# convert the object into a dict
required_the_test_to_update_dict = required_the_test_to_update_instance.to_dict()
# create an instance of RequiredTheTestToUpdate from a dict
required_the_test_to_update_from_dict = RequiredTheTestToUpdate.from_dict(required_the_test_to_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


