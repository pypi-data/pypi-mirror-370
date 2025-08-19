# ListBillingAccountSampleCreditResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[BillingAccountSampleCreditResponse]**](BillingAccountSampleCreditResponse.md) |  | 
**has_more** | **bool** |  | 

## Example

```python
from bugseq_client.openapi_client.models.list_billing_account_sample_credit_response import ListBillingAccountSampleCreditResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ListBillingAccountSampleCreditResponse from a JSON string
list_billing_account_sample_credit_response_instance = ListBillingAccountSampleCreditResponse.from_json(json)
# print the JSON string representation of the object
print(ListBillingAccountSampleCreditResponse.to_json())

# convert the object into a dict
list_billing_account_sample_credit_response_dict = list_billing_account_sample_credit_response_instance.to_dict()
# create an instance of ListBillingAccountSampleCreditResponse from a dict
list_billing_account_sample_credit_response_from_dict = ListBillingAccountSampleCreditResponse.from_dict(list_billing_account_sample_credit_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


