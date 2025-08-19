# JobRunResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**user_provided_name** | **str** |  | 
**owner_id** | **str** |  | 
**created** | **datetime** |  | 
**end_time** | **datetime** |  | 
**job_status** | [**JobStatus**](JobStatus.md) |  | 
**results_url** | **str** |  | 
**org_id** | **str** |  | 
**pipeline_version** | [**PipelineVersion**](PipelineVersion.md) |  | 

## Example

```python
from bugseq_client.openapi_client.models.job_run_response import JobRunResponse

# TODO update the JSON string below
json = "{}"
# create an instance of JobRunResponse from a JSON string
job_run_response_instance = JobRunResponse.from_json(json)
# print the JSON string representation of the object
print(JobRunResponse.to_json())

# convert the object into a dict
job_run_response_dict = job_run_response_instance.to_dict()
# create an instance of JobRunResponse from a dict
job_run_response_from_dict = JobRunResponse.from_dict(job_run_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


