# V1CreateLeaderboardRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**leaderboard** | [**V1Leaderboard**](V1Leaderboard.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_create_leaderboard_request import V1CreateLeaderboardRequest

# TODO update the JSON string below
json = "{}"
# create an instance of V1CreateLeaderboardRequest from a JSON string
v1_create_leaderboard_request_instance = V1CreateLeaderboardRequest.from_json(json)
# print the JSON string representation of the object
print(V1CreateLeaderboardRequest.to_json())

# convert the object into a dict
v1_create_leaderboard_request_dict = v1_create_leaderboard_request_instance.to_dict()
# create an instance of V1CreateLeaderboardRequest from a dict
v1_create_leaderboard_request_from_dict = V1CreateLeaderboardRequest.from_dict(v1_create_leaderboard_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


