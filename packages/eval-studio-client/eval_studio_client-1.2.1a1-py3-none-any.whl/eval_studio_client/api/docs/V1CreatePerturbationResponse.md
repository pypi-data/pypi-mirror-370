# V1CreatePerturbationResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**test_suite** | **str** | Perturbed test suite in JSON format. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_create_perturbation_response import V1CreatePerturbationResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1CreatePerturbationResponse from a JSON string
v1_create_perturbation_response_instance = V1CreatePerturbationResponse.from_json(json)
# print the JSON string representation of the object
print(V1CreatePerturbationResponse.to_json())

# convert the object into a dict
v1_create_perturbation_response_dict = v1_create_perturbation_response_instance.to_dict()
# create an instance of V1CreatePerturbationResponse from a dict
v1_create_perturbation_response_from_dict = V1CreatePerturbationResponse.from_dict(v1_create_perturbation_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


