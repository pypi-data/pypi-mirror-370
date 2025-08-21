# V1ListRAGCollectionsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**collections** | [**List[V1CollectionInfo]**](V1CollectionInfo.md) | Required. List of RAG collections available for evaluation. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_list_rag_collections_response import V1ListRAGCollectionsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListRAGCollectionsResponse from a JSON string
v1_list_rag_collections_response_instance = V1ListRAGCollectionsResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListRAGCollectionsResponse.to_json())

# convert the object into a dict
v1_list_rag_collections_response_dict = v1_list_rag_collections_response_instance.to_dict()
# create an instance of V1ListRAGCollectionsResponse from a dict
v1_list_rag_collections_response_from_dict = V1ListRAGCollectionsResponse.from_dict(v1_list_rag_collections_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


