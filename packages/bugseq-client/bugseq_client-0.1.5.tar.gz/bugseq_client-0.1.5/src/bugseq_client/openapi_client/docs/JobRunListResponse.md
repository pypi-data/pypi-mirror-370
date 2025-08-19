# JobRunListResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_runs** | [**List[JobRunResponse]**](JobRunResponse.md) |  | 
**has_more** | **bool** |  | 

## Example

```python
from bugseq_client.openapi_client.models.job_run_list_response import JobRunListResponse

# TODO update the JSON string below
json = "{}"
# create an instance of JobRunListResponse from a JSON string
job_run_list_response_instance = JobRunListResponse.from_json(json)
# print the JSON string representation of the object
print(JobRunListResponse.to_json())

# convert the object into a dict
job_run_list_response_dict = job_run_list_response_instance.to_dict()
# create an instance of JobRunListResponse from a dict
job_run_list_response_from_dict = JobRunListResponse.from_dict(job_run_list_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


