# V1ImportLeaderboardRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**test_lab_json** | **str** | Test Lab in JSON format. | [optional] 
**url** | **str** | URL pointing to a Test Lab in JSON format to import. | [optional] 
**evaluator** | **str** | Required. Resource name of the Evaluator used in this Leaderboard. | [optional] 
**model** | **str** | Required. Resource name of the Model used in this Leaderboard. | [optional] 
**test_display_name** | **str** | Required. Display name of the newly created Test. | [optional] 
**test_description** | **str** | Optional. Description of the newly created Test. | [optional] 
**leaderboard_display_name** | **str** | Required. Display name of the newly created Leaderboard. | [optional] 
**leaderboard_description** | **str** | Optional. Description of the newly created Leaderboard. | [optional] 
**leaderboard_type** | [**V1LeaderboardType**](V1LeaderboardType.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_import_leaderboard_request import V1ImportLeaderboardRequest

# TODO update the JSON string below
json = "{}"
# create an instance of V1ImportLeaderboardRequest from a JSON string
v1_import_leaderboard_request_instance = V1ImportLeaderboardRequest.from_json(json)
# print the JSON string representation of the object
print(V1ImportLeaderboardRequest.to_json())

# convert the object into a dict
v1_import_leaderboard_request_dict = v1_import_leaderboard_request_instance.to_dict()
# create an instance of V1ImportLeaderboardRequest from a dict
v1_import_leaderboard_request_from_dict = V1ImportLeaderboardRequest.from_dict(v1_import_leaderboard_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


