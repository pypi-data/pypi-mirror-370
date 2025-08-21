# V1ListTestCaseRelationshipsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**test_case_relationships** | [**List[V1TestCaseRelationship]**](V1TestCaseRelationship.md) | The TestCaseRelationships that were requested. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_list_test_case_relationships_response import V1ListTestCaseRelationshipsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListTestCaseRelationshipsResponse from a JSON string
v1_list_test_case_relationships_response_instance = V1ListTestCaseRelationshipsResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListTestCaseRelationshipsResponse.to_json())

# convert the object into a dict
v1_list_test_case_relationships_response_dict = v1_list_test_case_relationships_response_instance.to_dict()
# create an instance of V1ListTestCaseRelationshipsResponse from a dict
v1_list_test_case_relationships_response_from_dict = V1ListTestCaseRelationshipsResponse.from_dict(v1_list_test_case_relationships_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


