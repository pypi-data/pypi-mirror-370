# V1GetPerturbatorResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**perturbator** | [**V1Perturbator**](V1Perturbator.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_get_perturbator_response import V1GetPerturbatorResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1GetPerturbatorResponse from a JSON string
v1_get_perturbator_response_instance = V1GetPerturbatorResponse.from_json(json)
# print the JSON string representation of the object
print(V1GetPerturbatorResponse.to_json())

# convert the object into a dict
v1_get_perturbator_response_dict = v1_get_perturbator_response_instance.to_dict()
# create an instance of V1GetPerturbatorResponse from a dict
v1_get_perturbator_response_from_dict = V1GetPerturbatorResponse.from_dict(v1_get_perturbator_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


