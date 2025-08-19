# FileCreateS3Request


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**filename** | **str** |  | 
**s3_region** | **str** |  | [optional] 

## Example

```python
from bugseq_client.openapi_client.models.file_create_s3_request import FileCreateS3Request

# TODO update the JSON string below
json = "{}"
# create an instance of FileCreateS3Request from a JSON string
file_create_s3_request_instance = FileCreateS3Request.from_json(json)
# print the JSON string representation of the object
print(FileCreateS3Request.to_json())

# convert the object into a dict
file_create_s3_request_dict = file_create_s3_request_instance.to_dict()
# create an instance of FileCreateS3Request from a dict
file_create_s3_request_from_dict = FileCreateS3Request.from_dict(file_create_s3_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


