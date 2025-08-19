# JobRunFileResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**filename** | **str** |  | 
**size** | **int** |  | [optional] 

## Example

```python
from bugseq_client.openapi_client.models.job_run_file_response import JobRunFileResponse

# TODO update the JSON string below
json = "{}"
# create an instance of JobRunFileResponse from a JSON string
job_run_file_response_instance = JobRunFileResponse.from_json(json)
# print the JSON string representation of the object
print(JobRunFileResponse.to_json())

# convert the object into a dict
job_run_file_response_dict = job_run_file_response_instance.to_dict()
# create an instance of JobRunFileResponse from a dict
job_run_file_response_from_dict = JobRunFileResponse.from_dict(job_run_file_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


