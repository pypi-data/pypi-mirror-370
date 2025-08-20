# AddExporterToHost200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | Operation status | [optional] 
**message** | **str** | Detailed status message | [optional] 
**hostname** | **str** | Target hostname | [optional] 
**exporter** | [**AddExporterToHost200ResponseExporter**](AddExporterToHost200ResponseExporter.md) |  | [optional] 

## Example

```python
from ObservabilityAPI.models.add_exporter_to_host200_response import AddExporterToHost200Response

# TODO update the JSON string below
json = "{}"
# create an instance of AddExporterToHost200Response from a JSON string
add_exporter_to_host200_response_instance = AddExporterToHost200Response.from_json(json)
# print the JSON string representation of the object
print(AddExporterToHost200Response.to_json())

# convert the object into a dict
add_exporter_to_host200_response_dict = add_exporter_to_host200_response_instance.to_dict()
# create an instance of AddExporterToHost200Response from a dict
add_exporter_to_host200_response_from_dict = AddExporterToHost200Response.from_dict(add_exporter_to_host200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


