# V1Stats

Stats represents statistics about the Eval Studio instance, jobs and utilization.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**topic_modeling_pending_jobs** | **str** | Number of pending jobs in the topic modeling queue. It&#39;s marked as optional to always be part of the response, even when the value is zero. | [optional] 
**test_validation_pending_jobs** | **str** | Number of pending jobs in the test validation queue. It&#39;s marked as optional to always be part of the response, even when the value is zero. | [optional] 
**failure_clustering_pending_jobs** | **str** | Number of pending jobs in the failure clustering queue. It&#39;s marked as optional to always be part of the response, even when the value is zero. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_stats import V1Stats

# TODO update the JSON string below
json = "{}"
# create an instance of V1Stats from a JSON string
v1_stats_instance = V1Stats.from_json(json)
# print the JSON string representation of the object
print(V1Stats.to_json())

# convert the object into a dict
v1_stats_dict = v1_stats_instance.to_dict()
# create an instance of V1Stats from a dict
v1_stats_from_dict = V1Stats.from_dict(v1_stats_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


