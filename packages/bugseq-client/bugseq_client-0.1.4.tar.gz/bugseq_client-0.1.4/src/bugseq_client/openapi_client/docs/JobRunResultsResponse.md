# JobRunResultsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**user_provided_name** | **str** |  | [optional] 
**owner_id** | **str** |  | 
**created** | **datetime** |  | 
**end_time** | **datetime** |  | [optional] 
**job_status** | [**JobStatus**](JobStatus.md) |  | 
**inputs** | [**List[JobRunFileResponse]**](JobRunFileResponse.md) |  | 
**outputs** | [**List[JobRunFileResponse]**](JobRunFileResponse.md) |  | 
**org_id** | **str** |  | 
**pipeline_version** | [**PipelineVersion**](PipelineVersion.md) |  | 

## Example

```python
from bugseq_client.openapi_client.models.job_run_results_response import JobRunResultsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of JobRunResultsResponse from a JSON string
job_run_results_response_instance = JobRunResultsResponse.from_json(json)
# print the JSON string representation of the object
print(JobRunResultsResponse.to_json())

# convert the object into a dict
job_run_results_response_dict = job_run_results_response_instance.to_dict()
# create an instance of JobRunResultsResponse from a dict
job_run_results_response_from_dict = JobRunResultsResponse.from_dict(job_run_results_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


