# V1BatchGetLeaderboardsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**leaderboards** | [**List[V1Leaderboard]**](V1Leaderboard.md) | The requested Leaderboards. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_batch_get_leaderboards_response import V1BatchGetLeaderboardsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1BatchGetLeaderboardsResponse from a JSON string
v1_batch_get_leaderboards_response_instance = V1BatchGetLeaderboardsResponse.from_json(json)
# print the JSON string representation of the object
print(V1BatchGetLeaderboardsResponse.to_json())

# convert the object into a dict
v1_batch_get_leaderboards_response_dict = v1_batch_get_leaderboards_response_instance.to_dict()
# create an instance of V1BatchGetLeaderboardsResponse from a dict
v1_batch_get_leaderboards_response_from_dict = V1BatchGetLeaderboardsResponse.from_dict(v1_batch_get_leaderboards_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


