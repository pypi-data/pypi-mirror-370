# ObservabilityAPI.PrometheusApi

All URIs are relative to *http://localhost/PhrameObservability*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_exporter_to_host**](PrometheusApi.md#add_exporter_to_host) | **PUT** /prometheus | Add/Update Specific Exporter for Host
[**add_prometheus_target**](PrometheusApi.md#add_prometheus_target) | **POST** /prometheus | Add Prometheus Monitoring Target
[**get_prometheus_targets**](PrometheusApi.md#get_prometheus_targets) | **GET** /prometheus | Get Prometheus Targets Configuration
[**remove_prometheus_target**](PrometheusApi.md#remove_prometheus_target) | **DELETE** /prometheus | Remove Prometheus Monitoring Target


# **add_exporter_to_host**
> AddExporterToHost200Response add_exporter_to_host(hostname, ip_address, exporter_name, port, environment_label=environment_label)

Add/Update Specific Exporter for Host

Add or update a specific exporter for a given hostname in the Prometheus configuration. This allows fine-grained control over individual exporters without affecting others. If the hostname doesn't exist, it will be created. If the exporter already exists for the hostname, it will be updated. 

### Example


```python
import ObservabilityAPI
from ObservabilityAPI.models.add_exporter_to_host200_response import AddExporterToHost200Response
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
    api_instance = ObservabilityAPI.PrometheusApi(api_client)
    hostname = 'hostname_example' # str | Hostname or service name of the target system
    ip_address = 'ip_address_example' # str | IP address or hostname of the target system
    exporter_name = 'exporter_name_example' # str | Name of the exporter to add/update (e.g., node_exporter, process_exporter, cadvisor, custom_exporter)
    port = 56 # int | Port where the exporter metrics are exposed
    environment_label = '3adesign' # str | Environment or group label for dashboard categorization (optional) (default to '3adesign')

    try:
        # Add/Update Specific Exporter for Host
        api_response = api_instance.add_exporter_to_host(hostname, ip_address, exporter_name, port, environment_label=environment_label)
        print("The response of PrometheusApi->add_exporter_to_host:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrometheusApi->add_exporter_to_host: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **hostname** | **str**| Hostname or service name of the target system | 
 **ip_address** | **str**| IP address or hostname of the target system | 
 **exporter_name** | **str**| Name of the exporter to add/update (e.g., node_exporter, process_exporter, cadvisor, custom_exporter) | 
 **port** | **int**| Port where the exporter metrics are exposed | 
 **environment_label** | **str**| Environment or group label for dashboard categorization | [optional] [default to &#39;3adesign&#39;]

### Return type

[**AddExporterToHost200Response**](AddExporterToHost200Response.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Exporter added/updated successfully |  -  |
**400** | Bad Request - Invalid parameters |  -  |
**404** | Not Found - Prometheus instance not accessible |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_prometheus_target**
> AddPrometheusTarget200Response add_prometheus_target(hostname, ip_address, environment_label=environment_label, node_exporter_port=node_exporter_port, process_exporter_port=process_exporter_port, cadvisor_port=cadvisor_port)

Add Prometheus Monitoring Target

Add a new system to Prometheus monitoring configuration. Note: The target system must have the required metric exporters (Node Exporter, Process Exporter, cAdvisor)  properly configured and running on the specified ports for monitoring to work correctly.

### Example


```python
import ObservabilityAPI
from ObservabilityAPI.models.add_prometheus_target200_response import AddPrometheusTarget200Response
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
    api_instance = ObservabilityAPI.PrometheusApi(api_client)
    hostname = 'hostname_example' # str | Hostname or service name of the target system
    ip_address = 'ip_address_example' # str | IP address or hostname of the target system
    environment_label = '3adesign' # str | Environment or group label for dashboard categorization (optional) (default to '3adesign')
    node_exporter_port = '9100' # str | Port where Node Exporter metrics are exposed (optional) (default to '9100')
    process_exporter_port = '9099' # str | Port where Process Exporter metrics are exposed (optional) (default to '9099')
    cadvisor_port = '8082' # str | Port where cAdvisor container metrics are exposed (optional) (default to '8082')

    try:
        # Add Prometheus Monitoring Target
        api_response = api_instance.add_prometheus_target(hostname, ip_address, environment_label=environment_label, node_exporter_port=node_exporter_port, process_exporter_port=process_exporter_port, cadvisor_port=cadvisor_port)
        print("The response of PrometheusApi->add_prometheus_target:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrometheusApi->add_prometheus_target: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **hostname** | **str**| Hostname or service name of the target system | 
 **ip_address** | **str**| IP address or hostname of the target system | 
 **environment_label** | **str**| Environment or group label for dashboard categorization | [optional] [default to &#39;3adesign&#39;]
 **node_exporter_port** | **str**| Port where Node Exporter metrics are exposed | [optional] [default to &#39;9100&#39;]
 **process_exporter_port** | **str**| Port where Process Exporter metrics are exposed | [optional] [default to &#39;9099&#39;]
 **cadvisor_port** | **str**| Port where cAdvisor container metrics are exposed | [optional] [default to &#39;8082&#39;]

### Return type

[**AddPrometheusTarget200Response**](AddPrometheusTarget200Response.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Target added successfully |  -  |
**400** | Bad Request - Invalid parameters or target already exists |  -  |
**404** | Not Found - Prometheus instance not accessible |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_prometheus_targets**
> GetPrometheusTargets200Response get_prometheus_targets()

Get Prometheus Targets Configuration

Retrieve all configured Prometheus monitoring targets and their configurations

### Example


```python
import ObservabilityAPI
from ObservabilityAPI.models.get_prometheus_targets200_response import GetPrometheusTargets200Response
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
    api_instance = ObservabilityAPI.PrometheusApi(api_client)

    try:
        # Get Prometheus Targets Configuration
        api_response = api_instance.get_prometheus_targets()
        print("The response of PrometheusApi->get_prometheus_targets:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrometheusApi->get_prometheus_targets: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GetPrometheusTargets200Response**](GetPrometheusTargets200Response.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Prometheus targets retrieved successfully |  -  |
**400** | Bad Request - Invalid request parameters |  -  |
**404** | Not Found - No targets configured |  -  |
**500** | Internal Server Error |  -  |
**501** | Not Implemented - Feature not available |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **remove_prometheus_target**
> RemovePrometheusTarget200Response remove_prometheus_target(hostname)

Remove Prometheus Monitoring Target

Remove a monitoring target from the Prometheus configuration. This will stop collecting metrics from the specified system.

### Example


```python
import ObservabilityAPI
from ObservabilityAPI.models.remove_prometheus_target200_response import RemovePrometheusTarget200Response
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
    api_instance = ObservabilityAPI.PrometheusApi(api_client)
    hostname = 'hostname_example' # str | Hostname or service name of the target to be removed

    try:
        # Remove Prometheus Monitoring Target
        api_response = api_instance.remove_prometheus_target(hostname)
        print("The response of PrometheusApi->remove_prometheus_target:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrometheusApi->remove_prometheus_target: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **hostname** | **str**| Hostname or service name of the target to be removed | 

### Return type

[**RemovePrometheusTarget200Response**](RemovePrometheusTarget200Response.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Target removed successfully |  -  |
**400** | Bad Request - Invalid hostname parameter |  -  |
**404** | Not Found - Target does not exist |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

