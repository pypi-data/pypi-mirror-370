# JobRunSubmitRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_provided_name** | **str** |  | [optional] 
**aws_region** | **str** |  | 
**file_ids** | **List[str]** |  | 
**run_options** | [**RunOptionsRequest**](RunOptionsRequest.md) |  | 
**lab_id** | **str** |  | [optional] 
**testmode** | **bool** |  | [optional] [default to False]
**user_provided_metadata** | **List[Dict[str, JobRunSubmitRequestUserProvidedMetadataInnerValue]]** |  | [optional] 
**pipeline_version** | [**PipelineVersion**](PipelineVersion.md) |  | [optional] 

## Example

```python
from bugseq_client.openapi_client.models.job_run_submit_request import JobRunSubmitRequest

# TODO update the JSON string below
json = "{}"
# create an instance of JobRunSubmitRequest from a JSON string
job_run_submit_request_instance = JobRunSubmitRequest.from_json(json)
# print the JSON string representation of the object
print(JobRunSubmitRequest.to_json())

# convert the object into a dict
job_run_submit_request_dict = job_run_submit_request_instance.to_dict()
# create an instance of JobRunSubmitRequest from a dict
job_run_submit_request_from_dict = JobRunSubmitRequest.from_dict(job_run_submit_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


