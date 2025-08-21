# V1MetricScore

MetricScore represents the metric score.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**key** | **str** | Required. Metric key. | [optional] 
**value** | **float** | Required. Metric value - consider NaN, Infinity or -Infinity for float representation. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_metric_score import V1MetricScore

# TODO update the JSON string below
json = "{}"
# create an instance of V1MetricScore from a JSON string
v1_metric_score_instance = V1MetricScore.from_json(json)
# print the JSON string representation of the object
print(V1MetricScore.to_json())

# convert the object into a dict
v1_metric_score_dict = v1_metric_score_instance.to_dict()
# create an instance of V1MetricScore from a dict
v1_metric_score_from_dict = V1MetricScore.from_dict(v1_metric_score_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


