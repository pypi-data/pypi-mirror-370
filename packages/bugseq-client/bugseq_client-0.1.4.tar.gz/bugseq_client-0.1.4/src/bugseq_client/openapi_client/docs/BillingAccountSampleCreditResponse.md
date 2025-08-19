# BillingAccountSampleCreditResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**sample_type** | [**SampleTypeOutput**](SampleTypeOutput.md) |  | 
**initial_count** | **int** |  | 
**remaining_count** | **int** |  | 
**expiration** | **datetime** |  | 
**billing_account_id** | **str** |  | 
**created** | **datetime** |  | 

## Example

```python
from bugseq_client.openapi_client.models.billing_account_sample_credit_response import BillingAccountSampleCreditResponse

# TODO update the JSON string below
json = "{}"
# create an instance of BillingAccountSampleCreditResponse from a JSON string
billing_account_sample_credit_response_instance = BillingAccountSampleCreditResponse.from_json(json)
# print the JSON string representation of the object
print(BillingAccountSampleCreditResponse.to_json())

# convert the object into a dict
billing_account_sample_credit_response_dict = billing_account_sample_credit_response_instance.to_dict()
# create an instance of BillingAccountSampleCreditResponse from a dict
billing_account_sample_credit_response_from_dict = BillingAccountSampleCreditResponse.from_dict(billing_account_sample_credit_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


