# V1BatchGetModelsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**models** | [**List[V1Model]**](V1Model.md) | The Models that were requested. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_batch_get_models_response import V1BatchGetModelsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1BatchGetModelsResponse from a JSON string
v1_batch_get_models_response_instance = V1BatchGetModelsResponse.from_json(json)
# print the JSON string representation of the object
print(V1BatchGetModelsResponse.to_json())

# convert the object into a dict
v1_batch_get_models_response_dict = v1_batch_get_models_response_instance.to_dict()
# create an instance of V1BatchGetModelsResponse from a dict
v1_batch_get_models_response_from_dict = V1BatchGetModelsResponse.from_dict(v1_batch_get_models_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


