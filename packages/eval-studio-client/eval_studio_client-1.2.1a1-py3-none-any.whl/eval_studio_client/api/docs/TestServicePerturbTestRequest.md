# TestServicePerturbTestRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**perturbator_configurations** | [**List[V1PerturbatorConfiguration]**](V1PerturbatorConfiguration.md) | Required. PerturbatorConfigurations to apply to the Test. | [optional] 
**new_test_display_name** | **str** | Required. Name of the newly created test. | [optional] 
**new_test_description** | **str** | Optional. Description of the newly created Test. | [optional] 
**test_case_names** | **List[str]** | Optional. Perturbation apply only to selected testCases. | [optional] 

## Example

```python
from eval_studio_client.api.models.test_service_perturb_test_request import TestServicePerturbTestRequest

# TODO update the JSON string below
json = "{}"
# create an instance of TestServicePerturbTestRequest from a JSON string
test_service_perturb_test_request_instance = TestServicePerturbTestRequest.from_json(json)
# print the JSON string representation of the object
print(TestServicePerturbTestRequest.to_json())

# convert the object into a dict
test_service_perturb_test_request_dict = test_service_perturb_test_request_instance.to_dict()
# create an instance of TestServicePerturbTestRequest from a dict
test_service_perturb_test_request_from_dict = TestServicePerturbTestRequest.from_dict(test_service_perturb_test_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


