# DeployGrafanaDashboards200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Success message | [optional] 
**dashboards_deployed** | **List[str]** | List of deployed dashboard names | [optional] 

## Example

```python
from ObservabilityAPI.models.deploy_grafana_dashboards200_response import DeployGrafanaDashboards200Response

# TODO update the JSON string below
json = "{}"
# create an instance of DeployGrafanaDashboards200Response from a JSON string
deploy_grafana_dashboards200_response_instance = DeployGrafanaDashboards200Response.from_json(json)
# print the JSON string representation of the object
print(DeployGrafanaDashboards200Response.to_json())

# convert the object into a dict
deploy_grafana_dashboards200_response_dict = deploy_grafana_dashboards200_response_instance.to_dict()
# create an instance of DeployGrafanaDashboards200Response from a dict
deploy_grafana_dashboards200_response_from_dict = DeployGrafanaDashboards200Response.from_dict(deploy_grafana_dashboards200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


