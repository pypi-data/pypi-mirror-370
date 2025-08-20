# AddExporterToHost200ResponseExporter


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Exporter name | [optional] 
**port** | **int** | Exporter port | [optional] 

## Example

```python
from ObservabilityAPI.models.add_exporter_to_host200_response_exporter import AddExporterToHost200ResponseExporter

# TODO update the JSON string below
json = "{}"
# create an instance of AddExporterToHost200ResponseExporter from a JSON string
add_exporter_to_host200_response_exporter_instance = AddExporterToHost200ResponseExporter.from_json(json)
# print the JSON string representation of the object
print(AddExporterToHost200ResponseExporter.to_json())

# convert the object into a dict
add_exporter_to_host200_response_exporter_dict = add_exporter_to_host200_response_exporter_instance.to_dict()
# create an instance of AddExporterToHost200ResponseExporter from a dict
add_exporter_to_host200_response_exporter_from_dict = AddExporterToHost200ResponseExporter.from_dict(add_exporter_to_host200_response_exporter_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


