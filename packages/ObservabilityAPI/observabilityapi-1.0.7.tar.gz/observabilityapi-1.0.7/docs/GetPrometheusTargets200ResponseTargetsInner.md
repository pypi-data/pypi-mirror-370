# GetPrometheusTargets200ResponseTargetsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**host_name** | **str** | Target hostname | [optional] 
**ip_address** | **str** | Target IP address | [optional] 
**ports** | [**GetPrometheusTargets200ResponseTargetsInnerPorts**](GetPrometheusTargets200ResponseTargetsInnerPorts.md) |  | [optional] 

## Example

```python
from ObservabilityAPI.models.get_prometheus_targets200_response_targets_inner import GetPrometheusTargets200ResponseTargetsInner

# TODO update the JSON string below
json = "{}"
# create an instance of GetPrometheusTargets200ResponseTargetsInner from a JSON string
get_prometheus_targets200_response_targets_inner_instance = GetPrometheusTargets200ResponseTargetsInner.from_json(json)
# print the JSON string representation of the object
print(GetPrometheusTargets200ResponseTargetsInner.to_json())

# convert the object into a dict
get_prometheus_targets200_response_targets_inner_dict = get_prometheus_targets200_response_targets_inner_instance.to_dict()
# create an instance of GetPrometheusTargets200ResponseTargetsInner from a dict
get_prometheus_targets200_response_targets_inner_from_dict = GetPrometheusTargets200ResponseTargetsInner.from_dict(get_prometheus_targets200_response_targets_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


