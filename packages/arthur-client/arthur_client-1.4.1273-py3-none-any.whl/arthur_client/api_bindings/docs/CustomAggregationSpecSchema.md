# CustomAggregationSpecSchema


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of the custom aggregation function. | 
**description** | **str** |  | [optional] 
**reported_aggregations** | [**List[ReportedCustomAggregation]**](ReportedCustomAggregation.md) | Metadata for every aggregation the custom aggregation reports. | 
**aggregate_args** | [**List[CustomAggregationSpecSchemaAggregateArgsInner]**](CustomAggregationSpecSchemaAggregateArgsInner.md) | List of parameters to the custom aggregation&#39;s query function. | 
**sql** | **str** | DuckDBSQL query for the custom aggregation. | 
**id** | **str** | Unique identifier of the custom aggregation with version. | 
**workspace_id** | **str** | Unique identifier of the custom aggregation&#39;s parent workspace. | 
**version** | **int** | Version number of the custom aggregation function. | 
**authored_by** | [**User**](User.md) |  | 
**created_at** | **datetime** | Time of aggregation creation. | 

## Example

```python
from arthur_client.api_bindings.models.custom_aggregation_spec_schema import CustomAggregationSpecSchema

# TODO update the JSON string below
json = "{}"
# create an instance of CustomAggregationSpecSchema from a JSON string
custom_aggregation_spec_schema_instance = CustomAggregationSpecSchema.from_json(json)
# print the JSON string representation of the object
print(CustomAggregationSpecSchema.to_json())

# convert the object into a dict
custom_aggregation_spec_schema_dict = custom_aggregation_spec_schema_instance.to_dict()
# create an instance of CustomAggregationSpecSchema from a dict
custom_aggregation_spec_schema_from_dict = CustomAggregationSpecSchema.from_dict(custom_aggregation_spec_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


