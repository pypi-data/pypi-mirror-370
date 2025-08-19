# bugseq_client.openapi_client.BillingApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_billing_account_sample_credits_v1_billing_billing_account_id_credits_sample_get**](BillingApi.md#list_billing_account_sample_credits_v1_billing_billing_account_id_credits_sample_get) | **GET** /v1/billing/{billing_account_id}/credits/sample | List Billing Account Sample Credits


# **list_billing_account_sample_credits_v1_billing_billing_account_id_credits_sample_get**
> ListBillingAccountSampleCreditResponse list_billing_account_sample_credits_v1_billing_billing_account_id_credits_sample_get(billing_account_id, remaining_count_gt=remaining_count_gt, include_expired=include_expired, skip=skip, limit=limit, sort_dir=sort_dir, sort_by=sort_by)

List Billing Account Sample Credits

### Example

* Bearer Authentication (HTTPBearer):

```python
import bugseq_client.openapi_client
from bugseq_client.openapi_client.models.list_billing_account_sample_credit_response import ListBillingAccountSampleCreditResponse
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
    api_instance = bugseq_client.openapi_client.BillingApi(api_client)
    billing_account_id = 'billing_account_id_example' # str | 
    remaining_count_gt = 56 # int |  (optional)
    include_expired = True # bool |  (optional) (default to True)
    skip = 0 # int |  (optional) (default to 0)
    limit = 20 # int |  (optional) (default to 20)
    sort_dir = asc # str |  (optional) (default to asc)
    sort_by = expiration # str |  (optional) (default to expiration)

    try:
        # List Billing Account Sample Credits
        api_response = api_instance.list_billing_account_sample_credits_v1_billing_billing_account_id_credits_sample_get(billing_account_id, remaining_count_gt=remaining_count_gt, include_expired=include_expired, skip=skip, limit=limit, sort_dir=sort_dir, sort_by=sort_by)
        print("The response of BillingApi->list_billing_account_sample_credits_v1_billing_billing_account_id_credits_sample_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BillingApi->list_billing_account_sample_credits_v1_billing_billing_account_id_credits_sample_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **billing_account_id** | **str**|  | 
 **remaining_count_gt** | **int**|  | [optional] 
 **include_expired** | **bool**|  | [optional] [default to True]
 **skip** | **int**|  | [optional] [default to 0]
 **limit** | **int**|  | [optional] [default to 20]
 **sort_dir** | **str**|  | [optional] [default to asc]
 **sort_by** | **str**|  | [optional] [default to expiration]

### Return type

[**ListBillingAccountSampleCreditResponse**](ListBillingAccountSampleCreditResponse.md)

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

