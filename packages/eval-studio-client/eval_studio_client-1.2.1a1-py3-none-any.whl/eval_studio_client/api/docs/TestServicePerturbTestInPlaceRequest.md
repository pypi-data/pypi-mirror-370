# TestServicePerturbTestInPlaceRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**perturbator_configurations** | [**List[V1PerturbatorConfiguration]**](V1PerturbatorConfiguration.md) | Required. PerturbatorConfigurations to apply to the Test. | [optional] 
**test_case_names** | **List[str]** | Optional. Perturbation apply only to selected testCases. | [optional] 

## Example

```python
from eval_studio_client.api.models.test_service_perturb_test_in_place_request import TestServicePerturbTestInPlaceRequest

# TODO update the JSON string below
json = "{}"
# create an instance of TestServicePerturbTestInPlaceRequest from a JSON string
test_service_perturb_test_in_place_request_instance = TestServicePerturbTestInPlaceRequest.from_json(json)
# print the JSON string representation of the object
print(TestServicePerturbTestInPlaceRequest.to_json())

# convert the object into a dict
test_service_perturb_test_in_place_request_dict = test_service_perturb_test_in_place_request_instance.to_dict()
# create an instance of TestServicePerturbTestInPlaceRequest from a dict
test_service_perturb_test_in_place_request_from_dict = TestServicePerturbTestInPlaceRequest.from_dict(test_service_perturb_test_in_place_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


