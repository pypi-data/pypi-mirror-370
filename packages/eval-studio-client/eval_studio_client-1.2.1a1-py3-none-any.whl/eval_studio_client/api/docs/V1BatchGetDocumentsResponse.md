# V1BatchGetDocumentsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**documents** | [**List[V1Document]**](V1Document.md) | The Documents that were requested. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_batch_get_documents_response import V1BatchGetDocumentsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1BatchGetDocumentsResponse from a JSON string
v1_batch_get_documents_response_instance = V1BatchGetDocumentsResponse.from_json(json)
# print the JSON string representation of the object
print(V1BatchGetDocumentsResponse.to_json())

# convert the object into a dict
v1_batch_get_documents_response_dict = v1_batch_get_documents_response_instance.to_dict()
# create an instance of V1BatchGetDocumentsResponse from a dict
v1_batch_get_documents_response_from_dict = V1BatchGetDocumentsResponse.from_dict(v1_batch_get_documents_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


