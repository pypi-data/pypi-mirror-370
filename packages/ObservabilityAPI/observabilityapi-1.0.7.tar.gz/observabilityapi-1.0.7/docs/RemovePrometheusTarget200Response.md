# RemovePrometheusTarget200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Success message | [optional] 
**removed_target** | **str** | Name of the removed target | [optional] 

## Example

```python
from ObservabilityAPI.models.remove_prometheus_target200_response import RemovePrometheusTarget200Response

# TODO update the JSON string below
json = "{}"
# create an instance of RemovePrometheusTarget200Response from a JSON string
remove_prometheus_target200_response_instance = RemovePrometheusTarget200Response.from_json(json)
# print the JSON string representation of the object
print(RemovePrometheusTarget200Response.to_json())

# convert the object into a dict
remove_prometheus_target200_response_dict = remove_prometheus_target200_response_instance.to_dict()
# create an instance of RemovePrometheusTarget200Response from a dict
remove_prometheus_target200_response_from_dict = RemovePrometheusTarget200Response.from_dict(remove_prometheus_target200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


