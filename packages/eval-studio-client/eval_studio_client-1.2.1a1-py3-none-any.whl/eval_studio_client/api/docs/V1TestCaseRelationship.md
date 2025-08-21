# V1TestCaseRelationship


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**source** | **str** | Required. Source test case. | [optional] 
**target** | **str** | Required. Target test case. | [optional] 
**type** | **str** | Required. Type of the relationship. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_test_case_relationship import V1TestCaseRelationship

# TODO update the JSON string below
json = "{}"
# create an instance of V1TestCaseRelationship from a JSON string
v1_test_case_relationship_instance = V1TestCaseRelationship.from_json(json)
# print the JSON string representation of the object
print(V1TestCaseRelationship.to_json())

# convert the object into a dict
v1_test_case_relationship_dict = v1_test_case_relationship_instance.to_dict()
# create an instance of V1TestCaseRelationship from a dict
v1_test_case_relationship_from_dict = V1TestCaseRelationship.from_dict(v1_test_case_relationship_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


