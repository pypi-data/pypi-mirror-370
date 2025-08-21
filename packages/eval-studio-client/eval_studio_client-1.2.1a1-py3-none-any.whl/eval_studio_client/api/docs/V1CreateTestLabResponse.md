# V1CreateTestLabResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**test_lab** | [**V1TestLab**](V1TestLab.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_create_test_lab_response import V1CreateTestLabResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1CreateTestLabResponse from a JSON string
v1_create_test_lab_response_instance = V1CreateTestLabResponse.from_json(json)
# print the JSON string representation of the object
print(V1CreateTestLabResponse.to_json())

# convert the object into a dict
v1_create_test_lab_response_dict = v1_create_test_lab_response_instance.to_dict()
# create an instance of V1CreateTestLabResponse from a dict
v1_create_test_lab_response_from_dict = V1CreateTestLabResponse.from_dict(v1_create_test_lab_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


