# V1CheckBaseModelsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**model_availability** | **bool** | The model availability check. | [optional] 
**reason** | **str** | Optional. Information on why the model isn&#39;t available. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_check_base_models_response import V1CheckBaseModelsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1CheckBaseModelsResponse from a JSON string
v1_check_base_models_response_instance = V1CheckBaseModelsResponse.from_json(json)
# print the JSON string representation of the object
print(V1CheckBaseModelsResponse.to_json())

# convert the object into a dict
v1_check_base_models_response_dict = v1_check_base_models_response_instance.to_dict()
# create an instance of V1CheckBaseModelsResponse from a dict
v1_check_base_models_response_from_dict = V1CheckBaseModelsResponse.from_dict(v1_check_base_models_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


