# DbPhrameJSONStore

target resolution of a display

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**ui_config** | **str** |  | [optional] 

## Example

```python
from ObservabilityAPI.models.db_phrame_json_store import DbPhrameJSONStore

# TODO update the JSON string below
json = "{}"
# create an instance of DbPhrameJSONStore from a JSON string
db_phrame_json_store_instance = DbPhrameJSONStore.from_json(json)
# print the JSON string representation of the object
print(DbPhrameJSONStore.to_json())

# convert the object into a dict
db_phrame_json_store_dict = db_phrame_json_store_instance.to_dict()
# create an instance of DbPhrameJSONStore from a dict
db_phrame_json_store_from_dict = DbPhrameJSONStore.from_dict(db_phrame_json_store_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


