# V1GetModelResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**model** | [**V1Model**](V1Model.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_get_model_response import V1GetModelResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1GetModelResponse from a JSON string
v1_get_model_response_instance = V1GetModelResponse.from_json(json)
# print the JSON string representation of the object
print(V1GetModelResponse.to_json())

# convert the object into a dict
v1_get_model_response_dict = v1_get_model_response_instance.to_dict()
# create an instance of V1GetModelResponse from a dict
v1_get_model_response_from_dict = V1GetModelResponse.from_dict(v1_get_model_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


