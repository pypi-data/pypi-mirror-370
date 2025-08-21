# V1CreateTestResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**test** | [**V1Test**](V1Test.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_create_test_response import V1CreateTestResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1CreateTestResponse from a JSON string
v1_create_test_response_instance = V1CreateTestResponse.from_json(json)
# print the JSON string representation of the object
print(V1CreateTestResponse.to_json())

# convert the object into a dict
v1_create_test_response_dict = v1_create_test_response_instance.to_dict()
# create an instance of V1CreateTestResponse from a dict
v1_create_test_response_from_dict = V1CreateTestResponse.from_dict(v1_create_test_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


