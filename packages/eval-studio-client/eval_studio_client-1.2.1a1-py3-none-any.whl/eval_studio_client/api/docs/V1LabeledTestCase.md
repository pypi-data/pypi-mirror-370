# V1LabeledTestCase


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Required. The test case resource name. | [optional] 
**metric_value** | **float** | Required. The metric value. | [optional] 
**label** | **bool** | Required. Human label. True means the test case should be labeled as passed (positive), false means failed (negative). | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_labeled_test_case import V1LabeledTestCase

# TODO update the JSON string below
json = "{}"
# create an instance of V1LabeledTestCase from a JSON string
v1_labeled_test_case_instance = V1LabeledTestCase.from_json(json)
# print the JSON string representation of the object
print(V1LabeledTestCase.to_json())

# convert the object into a dict
v1_labeled_test_case_dict = v1_labeled_test_case_instance.to_dict()
# create an instance of V1LabeledTestCase from a dict
v1_labeled_test_case_from_dict = V1LabeledTestCase.from_dict(v1_labeled_test_case_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


