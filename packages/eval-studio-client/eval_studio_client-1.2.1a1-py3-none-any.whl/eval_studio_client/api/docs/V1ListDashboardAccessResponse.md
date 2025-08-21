# V1ListDashboardAccessResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**role_bindings** | [**List[V1RoleBinding]**](V1RoleBinding.md) | The RoleBindings for the Dashboard requested. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_list_dashboard_access_response import V1ListDashboardAccessResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListDashboardAccessResponse from a JSON string
v1_list_dashboard_access_response_instance = V1ListDashboardAccessResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListDashboardAccessResponse.to_json())

# convert the object into a dict
v1_list_dashboard_access_response_dict = v1_list_dashboard_access_response_instance.to_dict()
# create an instance of V1ListDashboardAccessResponse from a dict
v1_list_dashboard_access_response_from_dict = V1ListDashboardAccessResponse.from_dict(v1_list_dashboard_access_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


