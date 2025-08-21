# RequiredTheTestCaseToUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**create_time** | **datetime** | Output only. Timestamp when the Test was created. | [optional] [readonly] 
**creator** | **str** | Output only. Name of the user or service that requested creation of the TestCase. | [optional] [readonly] 
**update_time** | **datetime** | Output only. Optional. Timestamp when the TestCase was last updated. | [optional] [readonly] 
**updater** | **str** | Output only. Optional. Name of the user or service that requested update of the TestCase. | [optional] [readonly] 
**delete_time** | **datetime** | Output only. Optional. Set when the TestCase is deleted. When set TestCase should be considered as deleted. | [optional] [readonly] 
**deleter** | **str** | Output only. Optional. Name of the user or service that requested deletion of the TestCase. | [optional] [readonly] 
**parent** | **str** | Parent Test resource name. e.g.: \&quot;tests/&lt;UUID&gt;\&quot;. | [optional] 
**prompt** | **str** | Prompt text. Model input. | [optional] 
**answer** | **str** | Expected answer text. Model output. | [optional] 
**constraints** | **List[str]** | Constraints on the model output. | [optional] 
**condition** | **str** | Optional. Test case output condition, in a form of AIP-160 compliant filter expression. | [optional] 
**perturbed_by** | **List[str]** | Output only. The list of perturbators applied to this test case. | [optional] [readonly] 
**topics** | **List[str]** | Output only. The list of topics used to generate this test case. | [optional] [readonly] 
**generator** | [**V1TestCasesGenerator**](V1TestCasesGenerator.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.required_the_test_case_to_update import RequiredTheTestCaseToUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of RequiredTheTestCaseToUpdate from a JSON string
required_the_test_case_to_update_instance = RequiredTheTestCaseToUpdate.from_json(json)
# print the JSON string representation of the object
print(RequiredTheTestCaseToUpdate.to_json())

# convert the object into a dict
required_the_test_case_to_update_dict = required_the_test_case_to_update_instance.to_dict()
# create an instance of RequiredTheTestCaseToUpdate from a dict
required_the_test_case_to_update_from_dict = RequiredTheTestCaseToUpdate.from_dict(required_the_test_case_to_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


