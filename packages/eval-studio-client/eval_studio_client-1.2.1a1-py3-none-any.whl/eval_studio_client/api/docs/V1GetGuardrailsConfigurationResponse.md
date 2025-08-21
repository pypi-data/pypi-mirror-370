# V1GetGuardrailsConfigurationResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**guardrails_configuration_json** | **str** | The guardrails configuration for the Workflow requested in JSON format. This configuration is usable by the guardrails client as is. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_get_guardrails_configuration_response import V1GetGuardrailsConfigurationResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1GetGuardrailsConfigurationResponse from a JSON string
v1_get_guardrails_configuration_response_instance = V1GetGuardrailsConfigurationResponse.from_json(json)
# print the JSON string representation of the object
print(V1GetGuardrailsConfigurationResponse.to_json())

# convert the object into a dict
v1_get_guardrails_configuration_response_dict = v1_get_guardrails_configuration_response_instance.to_dict()
# create an instance of V1GetGuardrailsConfigurationResponse from a dict
v1_get_guardrails_configuration_response_from_dict = V1GetGuardrailsConfigurationResponse.from_dict(v1_get_guardrails_configuration_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


