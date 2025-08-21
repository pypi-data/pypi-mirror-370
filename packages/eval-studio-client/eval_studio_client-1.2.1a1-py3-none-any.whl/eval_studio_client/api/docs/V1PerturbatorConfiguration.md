# V1PerturbatorConfiguration

PerturbatorConfiguration represents the configuration of a perturbator to use during the perturbation process.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**intensity** | [**V1PerturbatorIntensity**](V1PerturbatorIntensity.md) |  | [optional] 
**params** | **str** | Optional. The parameters to pass to the perturbator. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_perturbator_configuration import V1PerturbatorConfiguration

# TODO update the JSON string below
json = "{}"
# create an instance of V1PerturbatorConfiguration from a JSON string
v1_perturbator_configuration_instance = V1PerturbatorConfiguration.from_json(json)
# print the JSON string representation of the object
print(V1PerturbatorConfiguration.to_json())

# convert the object into a dict
v1_perturbator_configuration_dict = v1_perturbator_configuration_instance.to_dict()
# create an instance of V1PerturbatorConfiguration from a dict
v1_perturbator_configuration_from_dict = V1PerturbatorConfiguration.from_dict(v1_perturbator_configuration_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


