{%- set start_time_defined = start_time is defined and start_time is not none  %}
{%- set end_time_defined = end_time is defined and end_time is not none  %}
{%- set partition_column_defined = partition_column is defined and partition_column is not none  %}

SELECT {{ ", ".join(select_columns) if select_columns is not none else "*" }} FROM (
    {{ source }}
)
{% if start_time_defined and end_time_defined %}
WHERE {{ timestamp_key }} >= from_iso8601_timestamp('{{ start_time }}') AND {{ timestamp_key }} < from_iso8601_timestamp('{{ end_time }}')
{% elif start_time_defined %}
WHERE {{ timestamp_key }} >= from_iso8601_timestamp('{{ start_time }}')
{% elif end_time_defined %}
WHERE {{ timestamp_key }} < from_iso8601_timestamp('{{ end_time }}')
{% endif %}
{% if partition_column_defined and partition_lower_bound is not none %}
AND {{ partition_column }} >= {{ partition_lower_bound }}
{% endif %}
{% if partition_column_defined and partition_upper_bound is not none %}
AND {{ partition_column }} <= {{ partition_upper_bound }}
{% endif %}
