# FileMultipartChunkInitUploadRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**file_id** | **str** |  | 
**upload_id** | **str** |  | 
**part_number** | **int** |  | 

## Example

```python
from bugseq_client.openapi_client.models.file_multipart_chunk_init_upload_request import FileMultipartChunkInitUploadRequest

# TODO update the JSON string below
json = "{}"
# create an instance of FileMultipartChunkInitUploadRequest from a JSON string
file_multipart_chunk_init_upload_request_instance = FileMultipartChunkInitUploadRequest.from_json(json)
# print the JSON string representation of the object
print(FileMultipartChunkInitUploadRequest.to_json())

# convert the object into a dict
file_multipart_chunk_init_upload_request_dict = file_multipart_chunk_init_upload_request_instance.to_dict()
# create an instance of FileMultipartChunkInitUploadRequest from a dict
file_multipart_chunk_init_upload_request_from_dict = FileMultipartChunkInitUploadRequest.from_dict(file_multipart_chunk_init_upload_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


