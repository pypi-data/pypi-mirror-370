# V1ListTestClassesResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**test_classes** | [**List[V1TestClass]**](V1TestClass.md) | The TestClasses that match the request. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_list_test_classes_response import V1ListTestClassesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListTestClassesResponse from a JSON string
v1_list_test_classes_response_instance = V1ListTestClassesResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListTestClassesResponse.to_json())

# convert the object into a dict
v1_list_test_classes_response_dict = v1_list_test_classes_response_instance.to_dict()
# create an instance of V1ListTestClassesResponse from a dict
v1_list_test_classes_response_from_dict = V1ListTestClassesResponse.from_dict(v1_list_test_classes_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


