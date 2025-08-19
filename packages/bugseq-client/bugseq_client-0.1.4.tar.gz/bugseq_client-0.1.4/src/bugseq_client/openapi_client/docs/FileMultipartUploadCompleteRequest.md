# FileMultipartUploadCompleteRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**file_id** | **str** |  | 
**upload_id** | **str** |  | 
**parts** | **object** |  | 

## Example

```python
from bugseq_client.openapi_client.models.file_multipart_upload_complete_request import FileMultipartUploadCompleteRequest

# TODO update the JSON string below
json = "{}"
# create an instance of FileMultipartUploadCompleteRequest from a JSON string
file_multipart_upload_complete_request_instance = FileMultipartUploadCompleteRequest.from_json(json)
# print the JSON string representation of the object
print(FileMultipartUploadCompleteRequest.to_json())

# convert the object into a dict
file_multipart_upload_complete_request_dict = file_multipart_upload_complete_request_instance.to_dict()
# create an instance of FileMultipartUploadCompleteRequest from a dict
file_multipart_upload_complete_request_from_dict = FileMultipartUploadCompleteRequest.from_dict(file_multipart_upload_complete_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


