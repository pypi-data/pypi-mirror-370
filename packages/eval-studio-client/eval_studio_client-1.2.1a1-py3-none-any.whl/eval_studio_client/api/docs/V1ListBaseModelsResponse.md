# V1ListBaseModelsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**base_models** | **List[str]** | The list of Models. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_list_base_models_response import V1ListBaseModelsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListBaseModelsResponse from a JSON string
v1_list_base_models_response_instance = V1ListBaseModelsResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListBaseModelsResponse.to_json())

# convert the object into a dict
v1_list_base_models_response_dict = v1_list_base_models_response_instance.to_dict()
# create an instance of V1ListBaseModelsResponse from a dict
v1_list_base_models_response_from_dict = V1ListBaseModelsResponse.from_dict(v1_list_base_models_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


