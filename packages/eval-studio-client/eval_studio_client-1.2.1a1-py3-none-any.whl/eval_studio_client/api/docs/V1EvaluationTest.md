# V1EvaluationTest

EvaluationTest defines a single test in a suite, with materialized corpus (documents) and test cases.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_urls** | **List[str]** | Optional. List of documents that create the context of the test. | [optional] 
**test_cases** | [**List[V1TestCase]**](V1TestCase.md) | Required. The test cases to run. | [optional] 
**test_case_relationships** | [**List[V1TestCaseRelationship]**](V1TestCaseRelationship.md) | Optional. List of relationships between test cases. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_evaluation_test import V1EvaluationTest

# TODO update the JSON string below
json = "{}"
# create an instance of V1EvaluationTest from a JSON string
v1_evaluation_test_instance = V1EvaluationTest.from_json(json)
# print the JSON string representation of the object
print(V1EvaluationTest.to_json())

# convert the object into a dict
v1_evaluation_test_dict = v1_evaluation_test_instance.to_dict()
# create an instance of V1EvaluationTest from a dict
v1_evaluation_test_from_dict = V1EvaluationTest.from_dict(v1_evaluation_test_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


