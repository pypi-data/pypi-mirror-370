# V1EstimateThresholdRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**operation** | **str** | Required. The Operation processing the estimation. | [optional] 
**original_threshold** | **float** | Required. Original threshold. | [optional] 
**evaluator** | **str** | Required. The evaluator resource name. | [optional] 
**metric** | **str** | Optional. The metric name. If no metric is provided, the evaluator&#39;s primary metric is used. | [optional] 
**train_set** | [**List[V1LabeledTestCase]**](V1LabeledTestCase.md) | Required. Test cases with metric value and labels used for estimating the threshold. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_estimate_threshold_request import V1EstimateThresholdRequest

# TODO update the JSON string below
json = "{}"
# create an instance of V1EstimateThresholdRequest from a JSON string
v1_estimate_threshold_request_instance = V1EstimateThresholdRequest.from_json(json)
# print the JSON string representation of the object
print(V1EstimateThresholdRequest.to_json())

# convert the object into a dict
v1_estimate_threshold_request_dict = v1_estimate_threshold_request_instance.to_dict()
# create an instance of V1EstimateThresholdRequest from a dict
v1_estimate_threshold_request_from_dict = V1EstimateThresholdRequest.from_dict(v1_estimate_threshold_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


