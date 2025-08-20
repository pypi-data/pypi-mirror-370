# GetPrometheusTargets200ResponseTargetsInnerPorts


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**node_exporter** | **str** |  | [optional] 
**process_exporter** | **str** |  | [optional] 
**cadvisor** | **str** |  | [optional] 

## Example

```python
from ObservabilityAPI.models.get_prometheus_targets200_response_targets_inner_ports import GetPrometheusTargets200ResponseTargetsInnerPorts

# TODO update the JSON string below
json = "{}"
# create an instance of GetPrometheusTargets200ResponseTargetsInnerPorts from a JSON string
get_prometheus_targets200_response_targets_inner_ports_instance = GetPrometheusTargets200ResponseTargetsInnerPorts.from_json(json)
# print the JSON string representation of the object
print(GetPrometheusTargets200ResponseTargetsInnerPorts.to_json())

# convert the object into a dict
get_prometheus_targets200_response_targets_inner_ports_dict = get_prometheus_targets200_response_targets_inner_ports_instance.to_dict()
# create an instance of GetPrometheusTargets200ResponseTargetsInnerPorts from a dict
get_prometheus_targets200_response_targets_inner_ports_from_dict = GetPrometheusTargets200ResponseTargetsInnerPorts.from_dict(get_prometheus_targets200_response_targets_inner_ports_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


