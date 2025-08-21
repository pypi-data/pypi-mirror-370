# V1ListDocumentsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**documents** | [**List[V1Document]**](V1Document.md) | The list of Documents. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_list_documents_response import V1ListDocumentsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of V1ListDocumentsResponse from a JSON string
v1_list_documents_response_instance = V1ListDocumentsResponse.from_json(json)
# print the JSON string representation of the object
print(V1ListDocumentsResponse.to_json())

# convert the object into a dict
v1_list_documents_response_dict = v1_list_documents_response_instance.to_dict()
# create an instance of V1ListDocumentsResponse from a dict
v1_list_documents_response_from_dict = V1ListDocumentsResponse.from_dict(v1_list_documents_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


