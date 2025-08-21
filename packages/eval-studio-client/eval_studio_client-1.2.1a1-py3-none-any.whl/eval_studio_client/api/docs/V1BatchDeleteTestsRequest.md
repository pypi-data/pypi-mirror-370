# V1BatchDeleteTestsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**names** | **List[str]** | The names of the Tests to delete. A maximum of 1000 can be specified. | [optional] 
**force** | **bool** | If set to true, any TestCases associated with the Tests will also be deleted. Otherwise, if any TestCases are associated with any of the Tests, the request will fail. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_batch_delete_tests_request import V1BatchDeleteTestsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of V1BatchDeleteTestsRequest from a JSON string
v1_batch_delete_tests_request_instance = V1BatchDeleteTestsRequest.from_json(json)
# print the JSON string representation of the object
print(V1BatchDeleteTestsRequest.to_json())

# convert the object into a dict
v1_batch_delete_tests_request_dict = v1_batch_delete_tests_request_instance.to_dict()
# create an instance of V1BatchDeleteTestsRequest from a dict
v1_batch_delete_tests_request_from_dict = V1BatchDeleteTestsRequest.from_dict(v1_batch_delete_tests_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


