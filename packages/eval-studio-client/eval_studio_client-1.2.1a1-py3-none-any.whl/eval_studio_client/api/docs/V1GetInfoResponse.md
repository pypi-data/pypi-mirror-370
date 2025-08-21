# V1GetInfoResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**info** | [**V1Info**](V1Info.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_get_info_response import V1GetInfoResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1GetInfoResponse from a JSON string
v1_get_info_response_instance = V1GetInfoResponse.from_json(json)
# print the JSON string representation of the object
print(V1GetInfoResponse.to_json())

# convert the object into a dict
v1_get_info_response_dict = v1_get_info_response_instance.to_dict()
# create an instance of V1GetInfoResponse from a dict
v1_get_info_response_from_dict = V1GetInfoResponse.from_dict(v1_get_info_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


