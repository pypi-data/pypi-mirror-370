# V1RoleBinding

RoleBinding is used to bind a user to a specific role for a specific resource.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**subject** | **str** | The subject to which the role is assigned. | [optional] 
**role** | [**V1Role**](V1Role.md) |  | [optional] 
**resource** | **str** | The resource to which the role is assigned. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_role_binding import V1RoleBinding

# TODO update the JSON string below
json = "{}"
# create an instance of V1RoleBinding from a JSON string
v1_role_binding_instance = V1RoleBinding.from_json(json)
# print the JSON string representation of the object
print(V1RoleBinding.to_json())

# convert the object into a dict
v1_role_binding_dict = v1_role_binding_instance.to_dict()
# create an instance of V1RoleBinding from a dict
v1_role_binding_from_dict = V1RoleBinding.from_dict(v1_role_binding_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


