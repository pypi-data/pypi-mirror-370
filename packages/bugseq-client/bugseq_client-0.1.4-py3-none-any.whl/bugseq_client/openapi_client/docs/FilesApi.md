# bugseq_client.openapi_client.FilesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**complete_multipart_upload_v1_files_multipart_complete_post**](FilesApi.md#complete_multipart_upload_v1_files_multipart_complete_post) | **POST** /v1/files/multipart/complete | Complete Multipart Upload
[**initialize_multipart_upload_v1_files_multipart_init_post**](FilesApi.md#initialize_multipart_upload_v1_files_multipart_init_post) | **POST** /v1/files/multipart/init | Initialize Multipart Upload
[**initialize_single_part_upload_v1_files_singlepart_init_post**](FilesApi.md#initialize_single_part_upload_v1_files_singlepart_init_post) | **POST** /v1/files/singlepart/init | Initialize Single Part Upload
[**presign_multipart_chunk_v1_files_multipart_chunk_post**](FilesApi.md#presign_multipart_chunk_v1_files_multipart_chunk_post) | **POST** /v1/files/multipart/chunk | Presign Multipart Chunk


# **complete_multipart_upload_v1_files_multipart_complete_post**
> object complete_multipart_upload_v1_files_multipart_complete_post(file_multipart_upload_complete_request)

Complete Multipart Upload

### Example

* Bearer Authentication (HTTPBearer):

```python
import bugseq_client.openapi_client
from bugseq_client.openapi_client.models.file_multipart_upload_complete_request import FileMultipartUploadCompleteRequest
from bugseq_client.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bugseq_client.openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: HTTPBearer
configuration = bugseq_client.openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with bugseq_client.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bugseq_client.openapi_client.FilesApi(api_client)
    file_multipart_upload_complete_request = bugseq_client.openapi_client.FileMultipartUploadCompleteRequest() # FileMultipartUploadCompleteRequest | 

    try:
        # Complete Multipart Upload
        api_response = api_instance.complete_multipart_upload_v1_files_multipart_complete_post(file_multipart_upload_complete_request)
        print("The response of FilesApi->complete_multipart_upload_v1_files_multipart_complete_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FilesApi->complete_multipart_upload_v1_files_multipart_complete_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_multipart_upload_complete_request** | [**FileMultipartUploadCompleteRequest**](FileMultipartUploadCompleteRequest.md)|  | 

### Return type

**object**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **initialize_multipart_upload_v1_files_multipart_init_post**
> FileInitUploadS3Response initialize_multipart_upload_v1_files_multipart_init_post(file_create_s3_request)

Initialize Multipart Upload

### Example

* Bearer Authentication (HTTPBearer):

```python
import bugseq_client.openapi_client
from bugseq_client.openapi_client.models.file_create_s3_request import FileCreateS3Request
from bugseq_client.openapi_client.models.file_init_upload_s3_response import FileInitUploadS3Response
from bugseq_client.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bugseq_client.openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: HTTPBearer
configuration = bugseq_client.openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with bugseq_client.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bugseq_client.openapi_client.FilesApi(api_client)
    file_create_s3_request = bugseq_client.openapi_client.FileCreateS3Request() # FileCreateS3Request | 

    try:
        # Initialize Multipart Upload
        api_response = api_instance.initialize_multipart_upload_v1_files_multipart_init_post(file_create_s3_request)
        print("The response of FilesApi->initialize_multipart_upload_v1_files_multipart_init_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FilesApi->initialize_multipart_upload_v1_files_multipart_init_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_create_s3_request** | [**FileCreateS3Request**](FileCreateS3Request.md)|  | 

### Return type

[**FileInitUploadS3Response**](FileInitUploadS3Response.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **initialize_single_part_upload_v1_files_singlepart_init_post**
> FileInitUploadS3Response initialize_single_part_upload_v1_files_singlepart_init_post(file_create_s3_request)

Initialize Single Part Upload

### Example

* Bearer Authentication (HTTPBearer):

```python
import bugseq_client.openapi_client
from bugseq_client.openapi_client.models.file_create_s3_request import FileCreateS3Request
from bugseq_client.openapi_client.models.file_init_upload_s3_response import FileInitUploadS3Response
from bugseq_client.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bugseq_client.openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: HTTPBearer
configuration = bugseq_client.openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with bugseq_client.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bugseq_client.openapi_client.FilesApi(api_client)
    file_create_s3_request = bugseq_client.openapi_client.FileCreateS3Request() # FileCreateS3Request | 

    try:
        # Initialize Single Part Upload
        api_response = api_instance.initialize_single_part_upload_v1_files_singlepart_init_post(file_create_s3_request)
        print("The response of FilesApi->initialize_single_part_upload_v1_files_singlepart_init_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FilesApi->initialize_single_part_upload_v1_files_singlepart_init_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_create_s3_request** | [**FileCreateS3Request**](FileCreateS3Request.md)|  | 

### Return type

[**FileInitUploadS3Response**](FileInitUploadS3Response.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **presign_multipart_chunk_v1_files_multipart_chunk_post**
> FileInitUploadS3Response presign_multipart_chunk_v1_files_multipart_chunk_post(file_multipart_chunk_init_upload_request)

Presign Multipart Chunk

### Example

* Bearer Authentication (HTTPBearer):

```python
import bugseq_client.openapi_client
from bugseq_client.openapi_client.models.file_init_upload_s3_response import FileInitUploadS3Response
from bugseq_client.openapi_client.models.file_multipart_chunk_init_upload_request import FileMultipartChunkInitUploadRequest
from bugseq_client.openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bugseq_client.openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: HTTPBearer
configuration = bugseq_client.openapi_client.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with bugseq_client.openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bugseq_client.openapi_client.FilesApi(api_client)
    file_multipart_chunk_init_upload_request = bugseq_client.openapi_client.FileMultipartChunkInitUploadRequest() # FileMultipartChunkInitUploadRequest | 

    try:
        # Presign Multipart Chunk
        api_response = api_instance.presign_multipart_chunk_v1_files_multipart_chunk_post(file_multipart_chunk_init_upload_request)
        print("The response of FilesApi->presign_multipart_chunk_v1_files_multipart_chunk_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FilesApi->presign_multipart_chunk_v1_files_multipart_chunk_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_multipart_chunk_init_upload_request** | [**FileMultipartChunkInitUploadRequest**](FileMultipartChunkInitUploadRequest.md)|  | 

### Return type

[**FileInitUploadS3Response**](FileInitUploadS3Response.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

