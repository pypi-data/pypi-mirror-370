# PerturbationServiceCreatePerturbationRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**perturbator_configurations** | [**List[V1PerturbatorConfiguration]**](V1PerturbatorConfiguration.md) | Required. PerturbatorConfiguration to apply to the parent Test. | [optional] 
**test_cases** | [**List[V1TestCase]**](V1TestCase.md) | Required. List of test cases to perturb. These are the test cases from the parent test.  TODO: breaks https://google.aip.dev/144 | [optional] 
**test_case_relationships** | [**List[V1TestCaseRelationship]**](V1TestCaseRelationship.md) | Optional. List of relationships between test cases. | [optional] 
**default_h2ogpte_model** | [**V1Model**](V1Model.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.perturbation_service_create_perturbation_request import PerturbationServiceCreatePerturbationRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PerturbationServiceCreatePerturbationRequest from a JSON string
perturbation_service_create_perturbation_request_instance = PerturbationServiceCreatePerturbationRequest.from_json(json)
# print the JSON string representation of the object
print(PerturbationServiceCreatePerturbationRequest.to_json())

# convert the object into a dict
perturbation_service_create_perturbation_request_dict = perturbation_service_create_perturbation_request_instance.to_dict()
# create an instance of PerturbationServiceCreatePerturbationRequest from a dict
perturbation_service_create_perturbation_request_from_dict = PerturbationServiceCreatePerturbationRequest.from_dict(perturbation_service_create_perturbation_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


