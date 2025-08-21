# V1GetLeaderboardResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**leaderboard** | [**V1Leaderboard**](V1Leaderboard.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_get_leaderboard_response import V1GetLeaderboardResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1GetLeaderboardResponse from a JSON string
v1_get_leaderboard_response_instance = V1GetLeaderboardResponse.from_json(json)
# print the JSON string representation of the object
print(V1GetLeaderboardResponse.to_json())

# convert the object into a dict
v1_get_leaderboard_response_dict = v1_get_leaderboard_response_instance.to_dict()
# create an instance of V1GetLeaderboardResponse from a dict
v1_get_leaderboard_response_from_dict = V1GetLeaderboardResponse.from_dict(v1_get_leaderboard_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


