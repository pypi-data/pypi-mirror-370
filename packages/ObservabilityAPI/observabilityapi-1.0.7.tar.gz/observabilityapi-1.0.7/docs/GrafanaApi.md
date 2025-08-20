# ObservabilityAPI.GrafanaApi

All URIs are relative to *http://localhost/PhrameObservability*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_grafana_datasource**](GrafanaApi.md#add_grafana_datasource) | **POST** /grafana/datasource | Add Datasource to Grafana
[**deploy_grafana_dashboards**](GrafanaApi.md#deploy_grafana_dashboards) | **GET** /grafana | Deploy Grafana Dashboards
[**generate_grafana_service_key**](GrafanaApi.md#generate_grafana_service_key) | **GET** /grafana/auth | Generate Grafana Service Account Key


# **add_grafana_datasource**
> AddGrafanaDatasource200Response add_grafana_datasource(datasource_name, datasource_type, datasource_url, service_key, database_name=database_name, username=username, password=password, is_default=is_default, basic_auth=basic_auth)

Add Datasource to Grafana

Add a new datasource to Grafana for metrics, logs, or other data visualization

### Example


```python
import ObservabilityAPI
from ObservabilityAPI.models.add_grafana_datasource200_response import AddGrafanaDatasource200Response
from ObservabilityAPI.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/PhrameObservability
# See configuration.py for a list of all supported configuration parameters.
configuration = ObservabilityAPI.Configuration(
    host = "http://localhost/PhrameObservability"
)


# Enter a context with an instance of the API client
with ObservabilityAPI.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = ObservabilityAPI.GrafanaApi(api_client)
    datasource_name = 'datasource_name_example' # str | Name for the datasource
    datasource_type = prometheus # str | Type of datasource to create (default to prometheus)
    datasource_url = 'datasource_url_example' # str | URL of the datasource endpoint
    service_key = 'service_key_example' # str | Grafana service account key for authentication
    database_name = 'database_name_example' # str | Database name (for database datasources) (optional)
    username = 'username_example' # str | Username for datasource authentication (optional)
    password = 'password_example' # str | Password for datasource authentication (optional)
    is_default = False # bool | Set this datasource as default (optional) (default to False)
    basic_auth = False # bool | Enable basic authentication (optional) (default to False)

    try:
        # Add Datasource to Grafana
        api_response = api_instance.add_grafana_datasource(datasource_name, datasource_type, datasource_url, service_key, database_name=database_name, username=username, password=password, is_default=is_default, basic_auth=basic_auth)
        print("The response of GrafanaApi->add_grafana_datasource:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling GrafanaApi->add_grafana_datasource: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **datasource_name** | **str**| Name for the datasource | 
 **datasource_type** | **str**| Type of datasource to create | [default to prometheus]
 **datasource_url** | **str**| URL of the datasource endpoint | 
 **service_key** | **str**| Grafana service account key for authentication | 
 **database_name** | **str**| Database name (for database datasources) | [optional] 
 **username** | **str**| Username for datasource authentication | [optional] 
 **password** | **str**| Password for datasource authentication | [optional] 
 **is_default** | **bool**| Set this datasource as default | [optional] [default to False]
 **basic_auth** | **bool**| Enable basic authentication | [optional] [default to False]

### Return type

[**AddGrafanaDatasource200Response**](AddGrafanaDatasource200Response.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Datasource added successfully |  -  |
**400** | Bad Request - Invalid parameters |  -  |
**401** | Unauthorized - Invalid Grafana credentials |  -  |
**404** | Not Found - Grafana instance not accessible |  -  |
**409** | Conflict - Datasource already exists |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deploy_grafana_dashboards**
> DeployGrafanaDashboards200Response deploy_grafana_dashboards(service_key)

Deploy Grafana Dashboards

Deploy container and machine metrics dashboards to the connected Grafana instance

### Example


```python
import ObservabilityAPI
from ObservabilityAPI.models.deploy_grafana_dashboards200_response import DeployGrafanaDashboards200Response
from ObservabilityAPI.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/PhrameObservability
# See configuration.py for a list of all supported configuration parameters.
configuration = ObservabilityAPI.Configuration(
    host = "http://localhost/PhrameObservability"
)


# Enter a context with an instance of the API client
with ObservabilityAPI.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = ObservabilityAPI.GrafanaApi(api_client)
    service_key = 'service_key_example' # str | Grafana service account key for authentication

    try:
        # Deploy Grafana Dashboards
        api_response = api_instance.deploy_grafana_dashboards(service_key)
        print("The response of GrafanaApi->deploy_grafana_dashboards:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling GrafanaApi->deploy_grafana_dashboards: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **service_key** | **str**| Grafana service account key for authentication | 

### Return type

[**DeployGrafanaDashboards200Response**](DeployGrafanaDashboards200Response.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Dashboards deployed successfully |  -  |
**400** | Bad Request - Invalid configuration |  -  |
**404** | Not Found - Grafana instance not accessible |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **generate_grafana_service_key**
> GenerateGrafanaServiceKey200Response generate_grafana_service_key(admin_username, admin_password, service_account_role, service_account_name=service_account_name)

Generate Grafana Service Account Key

Generate a service account key in Grafana that can be used as a bearer token for API authentication

### Example


```python
import ObservabilityAPI
from ObservabilityAPI.models.generate_grafana_service_key200_response import GenerateGrafanaServiceKey200Response
from ObservabilityAPI.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost/PhrameObservability
# See configuration.py for a list of all supported configuration parameters.
configuration = ObservabilityAPI.Configuration(
    host = "http://localhost/PhrameObservability"
)


# Enter a context with an instance of the API client
with ObservabilityAPI.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = ObservabilityAPI.GrafanaApi(api_client)
    admin_username = 'admin_username_example' # str | Grafana administrator username
    admin_password = 'admin_password_example' # str | Grafana administrator password
    service_account_role = Viewer # str | Role to assign to the service account (default to Viewer)
    service_account_name = 'service_account_name_example' # str | Name for the service account to be created (optional)

    try:
        # Generate Grafana Service Account Key
        api_response = api_instance.generate_grafana_service_key(admin_username, admin_password, service_account_role, service_account_name=service_account_name)
        print("The response of GrafanaApi->generate_grafana_service_key:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling GrafanaApi->generate_grafana_service_key: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **admin_username** | **str**| Grafana administrator username | 
 **admin_password** | **str**| Grafana administrator password | 
 **service_account_role** | **str**| Role to assign to the service account | [default to Viewer]
 **service_account_name** | **str**| Name for the service account to be created | [optional] 

### Return type

[**GenerateGrafanaServiceKey200Response**](GenerateGrafanaServiceKey200Response.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Service key generated successfully |  -  |
**400** | Bad Request - Invalid parameters |  -  |
**401** | Unauthorized - Invalid credentials |  -  |
**404** | Not Found - Grafana instance not accessible |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

