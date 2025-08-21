# V1ListMostRecentModelsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**models** | [**List[V1Model]**](V1Model.md) | The list of Models. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_list_most_recent_models_response import V1ListMostRecentModelsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListMostRecentModelsResponse from a JSON string
v1_list_most_recent_models_response_instance = V1ListMostRecentModelsResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListMostRecentModelsResponse.to_json())

# convert the object into a dict
v1_list_most_recent_models_response_dict = v1_list_most_recent_models_response_instance.to_dict()
# create an instance of V1ListMostRecentModelsResponse from a dict
v1_list_most_recent_models_response_from_dict = V1ListMostRecentModelsResponse.from_dict(v1_list_most_recent_models_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


