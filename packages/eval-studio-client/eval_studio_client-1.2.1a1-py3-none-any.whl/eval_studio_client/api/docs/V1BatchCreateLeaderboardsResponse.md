# V1BatchCreateLeaderboardsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**operation** | [**V1Operation**](V1Operation.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_batch_create_leaderboards_response import V1BatchCreateLeaderboardsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1BatchCreateLeaderboardsResponse from a JSON string
v1_batch_create_leaderboards_response_instance = V1BatchCreateLeaderboardsResponse.from_json(json)
# print the JSON string representation of the object
print(V1BatchCreateLeaderboardsResponse.to_json())

# convert the object into a dict
v1_batch_create_leaderboards_response_dict = v1_batch_create_leaderboards_response_instance.to_dict()
# create an instance of V1BatchCreateLeaderboardsResponse from a dict
v1_batch_create_leaderboards_response_from_dict = V1BatchCreateLeaderboardsResponse.from_dict(v1_batch_create_leaderboards_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


