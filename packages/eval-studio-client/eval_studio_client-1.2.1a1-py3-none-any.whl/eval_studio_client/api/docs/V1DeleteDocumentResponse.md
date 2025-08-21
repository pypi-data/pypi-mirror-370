# V1DeleteDocumentResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document** | [**V1Document**](V1Document.md) |  | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_delete_document_response import V1DeleteDocumentResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1DeleteDocumentResponse from a JSON string
v1_delete_document_response_instance = V1DeleteDocumentResponse.from_json(json)
# print the JSON string representation of the object
print(V1DeleteDocumentResponse.to_json())

# convert the object into a dict
v1_delete_document_response_dict = v1_delete_document_response_instance.to_dict()
# create an instance of V1DeleteDocumentResponse from a dict
v1_delete_document_response_from_dict = V1DeleteDocumentResponse.from_dict(v1_delete_document_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


