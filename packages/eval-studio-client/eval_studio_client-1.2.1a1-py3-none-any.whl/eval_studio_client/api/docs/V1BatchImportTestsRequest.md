# V1BatchImportTestsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tests_json** | **str** | Tests in JSON format. | [optional] 
**url** | **str** | URL pointing to the Tests in JSON format to import. | [optional] 
**test_display_name_prefix** | **str** | Required. Display name prefix of the newly created Test. If more than one Test is to be created, the display name of second and following Tests will be the display name prefix followed by a number. | [optional] 
**test_description** | **str** | Optional. Description of the newly created Tests. | [optional] 

## Example

```python
from eval_studio_client.api.models.v1_batch_import_tests_request import V1BatchImportTestsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of V1BatchImportTestsRequest from a JSON string
v1_batch_import_tests_request_instance = V1BatchImportTestsRequest.from_json(json)
# print the JSON string representation of the object
print(V1BatchImportTestsRequest.to_json())

# convert the object into a dict
v1_batch_import_tests_request_dict = v1_batch_import_tests_request_instance.to_dict()
# create an instance of V1BatchImportTestsRequest from a dict
v1_batch_import_tests_request_from_dict = V1BatchImportTestsRequest.from_dict(v1_batch_import_tests_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


