# V1MetricScores


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**scores** | [**List[V1MetricScore]**](V1MetricScore.md) | Required. The metric scores. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_metric_scores import V1MetricScores

# TODO update the JSON string below
json = "{}"
# create an instance of V1MetricScores from a JSON string
v1_metric_scores_instance = V1MetricScores.from_json(json)
# print the JSON string representation of the object
print(V1MetricScores.to_json())

# convert the object into a dict
v1_metric_scores_dict = v1_metric_scores_instance.to_dict()
# create an instance of V1MetricScores from a dict
v1_metric_scores_from_dict = V1MetricScores.from_dict(v1_metric_scores_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


