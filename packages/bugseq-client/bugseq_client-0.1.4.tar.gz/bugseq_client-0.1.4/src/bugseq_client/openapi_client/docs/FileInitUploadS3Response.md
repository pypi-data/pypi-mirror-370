# FileInitUploadS3Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**presigned_s3_data** | **object** |  | 

## Example

```python
from bugseq_client.openapi_client.models.file_init_upload_s3_response import FileInitUploadS3Response

# TODO update the JSON string below
json = "{}"
# create an instance of FileInitUploadS3Response from a JSON string
file_init_upload_s3_response_instance = FileInitUploadS3Response.from_json(json)
# print the JSON string representation of the object
print(FileInitUploadS3Response.to_json())

# convert the object into a dict
file_init_upload_s3_response_dict = file_init_upload_s3_response_instance.to_dict()
# create an instance of FileInitUploadS3Response from a dict
file_init_upload_s3_response_from_dict = FileInitUploadS3Response.from_dict(file_init_upload_s3_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


