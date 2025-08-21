# V1WorkflowNodeAttributes

WorkflowNodeAttributes represents additional attributes of a WorkflowNode.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**can_delete** | **bool** | Whether the WorkflowNode can be deleted. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_workflow_node_attributes import V1WorkflowNodeAttributes

# TODO update the JSON string below
json = "{}"
# create an instance of V1WorkflowNodeAttributes from a JSON string
v1_workflow_node_attributes_instance = V1WorkflowNodeAttributes.from_json(json)
# print the JSON string representation of the object
print(V1WorkflowNodeAttributes.to_json())

# convert the object into a dict
v1_workflow_node_attributes_dict = v1_workflow_node_attributes_instance.to_dict()
# create an instance of V1WorkflowNodeAttributes from a dict
v1_workflow_node_attributes_from_dict = V1WorkflowNodeAttributes.from_dict(v1_workflow_node_attributes_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


