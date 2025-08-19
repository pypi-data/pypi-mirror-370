# RunOptionsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**platform** | [**Platform**](Platform.md) |  | 
**kit** | [**Kit**](Kit.md) |  | [optional] 
**metagenomic_database** | [**MetagenomicDatabase**](MetagenomicDatabase.md) |  | [optional] 
**sample_type** | [**SampleTypeInput**](SampleTypeInput.md) |  | 
**molecule_type** | [**MoleculeType**](MoleculeType.md) |  | [optional] 
**include_in_lab_db** | **bool** |  | [optional] [default to True]
**filter_animal_reads** | **bool** |  | [optional] 

## Example

```python
from bugseq_client.openapi_client.models.run_options_request import RunOptionsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RunOptionsRequest from a JSON string
run_options_request_instance = RunOptionsRequest.from_json(json)
# print the JSON string representation of the object
print(RunOptionsRequest.to_json())

# convert the object into a dict
run_options_request_dict = run_options_request_instance.to_dict()
# create an instance of RunOptionsRequest from a dict
run_options_request_from_dict = RunOptionsRequest.from_dict(run_options_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


