# V1ListPerturbatorsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**perturbators** | [**List[V1Perturbator]**](V1Perturbator.md) | The list of Perturbators. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_list_perturbators_response import V1ListPerturbatorsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListPerturbatorsResponse from a JSON string
v1_list_perturbators_response_instance = V1ListPerturbatorsResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListPerturbatorsResponse.to_json())

# convert the object into a dict
v1_list_perturbators_response_dict = v1_list_perturbators_response_instance.to_dict()
# create an instance of V1ListPerturbatorsResponse from a dict
v1_list_perturbators_response_from_dict = V1ListPerturbatorsResponse.from_dict(v1_list_perturbators_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


