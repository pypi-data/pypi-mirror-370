# GenerateGrafanaServiceKey200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**service_key** | **str** | Generated service account key | [optional] 
**message** | **str** | Success message | [optional] 

## Example

```python
from ObservabilityAPI.models.generate_grafana_service_key200_response import GenerateGrafanaServiceKey200Response

# TODO update the JSON string below
json = "{}"
# create an instance of GenerateGrafanaServiceKey200Response from a JSON string
generate_grafana_service_key200_response_instance = GenerateGrafanaServiceKey200Response.from_json(json)
# print the JSON string representation of the object
print(GenerateGrafanaServiceKey200Response.to_json())

# convert the object into a dict
generate_grafana_service_key200_response_dict = generate_grafana_service_key200_response_instance.to_dict()
# create an instance of GenerateGrafanaServiceKey200Response from a dict
generate_grafana_service_key200_response_from_dict = GenerateGrafanaServiceKey200Response.from_dict(generate_grafana_service_key200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


