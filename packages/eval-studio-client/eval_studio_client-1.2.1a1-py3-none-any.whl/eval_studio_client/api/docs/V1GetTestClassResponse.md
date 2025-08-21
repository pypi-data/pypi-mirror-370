# V1GetTestClassResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**test_class** | [**V1TestClass**](V1TestClass.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_get_test_class_response import V1GetTestClassResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1GetTestClassResponse from a JSON string
v1_get_test_class_response_instance = V1GetTestClassResponse.from_json(json)
# print the JSON string representation of the object
print(V1GetTestClassResponse.to_json())

# convert the object into a dict
v1_get_test_class_response_dict = v1_get_test_class_response_instance.to_dict()
# create an instance of V1GetTestClassResponse from a dict
v1_get_test_class_response_from_dict = V1GetTestClassResponse.from_dict(v1_get_test_class_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


