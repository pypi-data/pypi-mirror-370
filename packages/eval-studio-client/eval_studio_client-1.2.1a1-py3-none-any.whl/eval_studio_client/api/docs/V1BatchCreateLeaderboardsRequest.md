# V1BatchCreateLeaderboardsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**requests** | [**List[V1CreateLeaderboardRequest]**](V1CreateLeaderboardRequest.md) | Required. Contains list of requests for leaderboards to be created. | [optional] 
**dashboard_display_name** | **str** | Optional. Display name for the dashboard that will group the leaderboards. | [optional] 
**dashboard_description** | **str** | Optional. Description for the dashboard that will group the leaderboards. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_batch_create_leaderboards_request import V1BatchCreateLeaderboardsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of V1BatchCreateLeaderboardsRequest from a JSON string
v1_batch_create_leaderboards_request_instance = V1BatchCreateLeaderboardsRequest.from_json(json)
# print the JSON string representation of the object
print(V1BatchCreateLeaderboardsRequest.to_json())

# convert the object into a dict
v1_batch_create_leaderboards_request_dict = v1_batch_create_leaderboards_request_instance.to_dict()
# create an instance of V1BatchCreateLeaderboardsRequest from a dict
v1_batch_create_leaderboards_request_from_dict = V1BatchCreateLeaderboardsRequest.from_dict(v1_batch_create_leaderboards_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


