{%- set is_partitioned = partition_by is defined and partition_by is not none  %}
{%- set is_hash_provided = tecton_table_metadata_hash is defined and tecton_table_metadata_hash is not none  %}
{%- set is_versioned = tecton_table_spec_version is defined and tecton_table_spec_version is not none %}

CREATE EXTERNAL TABLE IF NOT EXISTS `{{ database }}`.`{{ table }}` (

{%- for col_name, type_name in columns.items() %}
    `{{ col_name }}` {{ type_name }}{%- if not loop.last %}, {%- endif %}
{%- endfor %}

)
{%- if is_partitioned %}
{%- if partition_by_type == "integer" %}
PARTITIONED BY(`{{ partition_by }}` bigint)
{%- else %}
PARTITIONED BY(`{{ partition_by }}` string)
{%- endif %}
{%- endif %}

{%- if offline_store_type == "parquet" %}
ROW FORMAT SERDE 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
WITH SERDEPROPERTIES (
'serialization.format' = '1'
)
LOCATION '{{ s3_location }}'
{%- elif offline_store_type == "delta" %}
ROW FORMAT SERDE 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
STORED AS INPUTFORMAT 'org.apache.hadoop.hive.ql.io.SymlinkTextInputFormat'
OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION '{{ s3_location }}/_symlink_format_manifest/'
{%- endif %}

TBLPROPERTIES (
'has_encrypted_data'='false'
{%- if is_hash_provided %}
,'tecton_table_metadata_hash'='{{tecton_table_metadata_hash}}'
{%- endif %}
{%- if is_versioned %}
,'tecton_table_spec_version'='{{tecton_table_spec_version}}'
{%- endif %}
{%- if is_partitioned %}
,'projection.enabled'='true',
'projection.{{ partition_by }}.type'='{{ partition_by_type }}',
'projection.{{ partition_by }}.range'='{{ partition_by_range_from }},{{ partition_by_range_to }}'
{%- if partition_by_format %}
,'projection.{{ partition_by }}.format'='{{ partition_by_format }}'
{%- endif %}

{%- if partition_by_interval %}
,'projection.{{ partition_by }}.interval'='{{ partition_by_interval }}'
{%- endif %}

{%- endif %}
);
