# GetPrometheusTargets200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**targets** | [**List[GetPrometheusTargets200ResponseTargetsInner]**](GetPrometheusTargets200ResponseTargetsInner.md) |  | [optional] 
**message** | **str** | Response message | [optional] 

## Example

```python
from ObservabilityAPI.models.get_prometheus_targets200_response import GetPrometheusTargets200Response

# TODO update the JSON string below
json = "{}"
# create an instance of GetPrometheusTargets200Response from a JSON string
get_prometheus_targets200_response_instance = GetPrometheusTargets200Response.from_json(json)
# print the JSON string representation of the object
print(GetPrometheusTargets200Response.to_json())

# convert the object into a dict
get_prometheus_targets200_response_dict = get_prometheus_targets200_response_instance.to_dict()
# create an instance of GetPrometheusTargets200Response from a dict
get_prometheus_targets200_response_from_dict = GetPrometheusTargets200Response.from_dict(get_prometheus_targets200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


