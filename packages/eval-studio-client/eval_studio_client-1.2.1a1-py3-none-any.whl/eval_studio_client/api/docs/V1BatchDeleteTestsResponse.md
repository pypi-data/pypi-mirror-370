# V1BatchDeleteTestsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tests** | [**List[V1Test]**](V1Test.md) | The deleted Tests. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_batch_delete_tests_response import V1BatchDeleteTestsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1BatchDeleteTestsResponse from a JSON string
v1_batch_delete_tests_response_instance = V1BatchDeleteTestsResponse.from_json(json)
# print the JSON string representation of the object
print(V1BatchDeleteTestsResponse.to_json())

# convert the object into a dict
v1_batch_delete_tests_response_dict = v1_batch_delete_tests_response_instance.to_dict()
# create an instance of V1BatchDeleteTestsResponse from a dict
v1_batch_delete_tests_response_from_dict = V1BatchDeleteTestsResponse.from_dict(v1_batch_delete_tests_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


