# AddGrafanaDatasource200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Success message | [optional] 
**datasource_id** | **int** | ID of the created datasource | [optional] 
**datasource_name** | **str** | Name of the created datasource | [optional] 

## Example

```python
from ObservabilityAPI.models.add_grafana_datasource200_response import AddGrafanaDatasource200Response

# TODO update the JSON string below
json = "{}"
# create an instance of AddGrafanaDatasource200Response from a JSON string
add_grafana_datasource200_response_instance = AddGrafanaDatasource200Response.from_json(json)
# print the JSON string representation of the object
print(AddGrafanaDatasource200Response.to_json())

# convert the object into a dict
add_grafana_datasource200_response_dict = add_grafana_datasource200_response_instance.to_dict()
# create an instance of AddGrafanaDatasource200Response from a dict
add_grafana_datasource200_response_from_dict = AddGrafanaDatasource200Response.from_dict(add_grafana_datasource200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


