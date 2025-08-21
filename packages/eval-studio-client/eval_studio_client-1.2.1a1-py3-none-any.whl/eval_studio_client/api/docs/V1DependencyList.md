# V1DependencyList


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**node** | **str** | The name of the Workflow Node to retrieve dependencies for. | [optional] 
**dependencies** | [**List[V1WorkflowDependency]**](V1WorkflowDependency.md) | The names of the Workflow Node dependencies. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_dependency_list import V1DependencyList

# TODO update the JSON string below
json = "{}"
# create an instance of V1DependencyList from a JSON string
v1_dependency_list_instance = V1DependencyList.from_json(json)
# print the JSON string representation of the object
print(V1DependencyList.to_json())

# convert the object into a dict
v1_dependency_list_dict = v1_dependency_list_instance.to_dict()
# create an instance of V1DependencyList from a dict
v1_dependency_list_from_dict = V1DependencyList.from_dict(v1_dependency_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


