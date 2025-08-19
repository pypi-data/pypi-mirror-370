# bugseq_client.openapi_client.JobsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**download_analysis_result_v1_jobs_job_id_results_download_get**](JobsApi.md#download_analysis_result_v1_jobs_job_id_results_download_get) | **GET** /v1/jobs/{job_id}/results/download | Download Analysis Result
[**get_analysis_results_v1_jobs_job_id_results_get**](JobsApi.md#get_analysis_results_v1_jobs_job_id_results_get) | **GET** /v1/jobs/{job_id}/results | Get Analysis Results
[**list_analyses_v1_jobs_get**](JobsApi.md#list_analyses_v1_jobs_get) | **GET** /v1/jobs/ | List Analyses
[**submit_analysis_v1_jobs_post**](JobsApi.md#submit_analysis_v1_jobs_post) | **POST** /v1/jobs/ | Submit Analysis


# **download_analysis_result_v1_jobs_job_id_results_download_get**
> FileDownloadResponse download_analysis_result_v1_jobs_job_id_results_download_get(job_id, filename)

Download Analysis Result

### Example

* Bearer Authentication (HTTPBearer):

```python
import bugseq_client.openapi_client
from bugseq_client.openapi_client.models.file_download_response import FileDownloadResponse
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
    api_instance = bugseq_client.openapi_client.JobsApi(api_client)
    job_id = 'job_id_example' # str | 
    filename = 'filename_example' # str | 

    try:
        # Download Analysis Result
        api_response = api_instance.download_analysis_result_v1_jobs_job_id_results_download_get(job_id, filename)
        print("The response of JobsApi->download_analysis_result_v1_jobs_job_id_results_download_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling JobsApi->download_analysis_result_v1_jobs_job_id_results_download_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 
 **filename** | **str**|  | 

### Return type

[**FileDownloadResponse**](FileDownloadResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_analysis_results_v1_jobs_job_id_results_get**
> JobRunResultsResponse get_analysis_results_v1_jobs_job_id_results_get(job_id)

Get Analysis Results

### Example

* Bearer Authentication (HTTPBearer):

```python
import bugseq_client.openapi_client
from bugseq_client.openapi_client.models.job_run_results_response import JobRunResultsResponse
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
    api_instance = bugseq_client.openapi_client.JobsApi(api_client)
    job_id = 'job_id_example' # str | 

    try:
        # Get Analysis Results
        api_response = api_instance.get_analysis_results_v1_jobs_job_id_results_get(job_id)
        print("The response of JobsApi->get_analysis_results_v1_jobs_job_id_results_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling JobsApi->get_analysis_results_v1_jobs_job_id_results_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 

### Return type

[**JobRunResultsResponse**](JobRunResultsResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_analyses_v1_jobs_get**
> JobRunListResponse list_analyses_v1_jobs_get(ids=ids, owner_ids=owner_ids, lab_ids=lab_ids, user_provided_name=user_provided_name, skip=skip, limit=limit)

List Analyses

### Example

* Bearer Authentication (HTTPBearer):

```python
import bugseq_client.openapi_client
from bugseq_client.openapi_client.models.job_run_list_response import JobRunListResponse
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
    api_instance = bugseq_client.openapi_client.JobsApi(api_client)
    ids = ['ids_example'] # List[Optional[str]] |  (optional)
    owner_ids = ['owner_ids_example'] # List[str] |  (optional)
    lab_ids = ['lab_ids_example'] # List[str] |  (optional)
    user_provided_name = 'user_provided_name_example' # str |  (optional)
    skip = 0 # int |  (optional) (default to 0)
    limit = 20 # int |  (optional) (default to 20)

    try:
        # List Analyses
        api_response = api_instance.list_analyses_v1_jobs_get(ids=ids, owner_ids=owner_ids, lab_ids=lab_ids, user_provided_name=user_provided_name, skip=skip, limit=limit)
        print("The response of JobsApi->list_analyses_v1_jobs_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling JobsApi->list_analyses_v1_jobs_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **ids** | [**List[Optional[str]]**](str.md)|  | [optional] 
 **owner_ids** | [**List[str]**](str.md)|  | [optional] 
 **lab_ids** | [**List[str]**](str.md)|  | [optional] 
 **user_provided_name** | **str**|  | [optional] 
 **skip** | **int**|  | [optional] [default to 0]
 **limit** | **int**|  | [optional] [default to 20]

### Return type

[**JobRunListResponse**](JobRunListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **submit_analysis_v1_jobs_post**
> JobRunSubmitResponse submit_analysis_v1_jobs_post(job_run_submit_request)

Submit Analysis

### Example

* Bearer Authentication (HTTPBearer):

```python
import bugseq_client.openapi_client
from bugseq_client.openapi_client.models.job_run_submit_request import JobRunSubmitRequest
from bugseq_client.openapi_client.models.job_run_submit_response import JobRunSubmitResponse
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
    api_instance = bugseq_client.openapi_client.JobsApi(api_client)
    job_run_submit_request = bugseq_client.openapi_client.JobRunSubmitRequest() # JobRunSubmitRequest | 

    try:
        # Submit Analysis
        api_response = api_instance.submit_analysis_v1_jobs_post(job_run_submit_request)
        print("The response of JobsApi->submit_analysis_v1_jobs_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling JobsApi->submit_analysis_v1_jobs_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_run_submit_request** | [**JobRunSubmitRequest**](JobRunSubmitRequest.md)|  | 

### Return type

[**JobRunSubmitResponse**](JobRunSubmitResponse.md)

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

