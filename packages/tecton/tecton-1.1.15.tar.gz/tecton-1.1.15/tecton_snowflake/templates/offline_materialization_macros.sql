{%- macro delete_materialized_data_within_range(destination_table, start_time, end_time, continuous, slide_interval, is_aggregate, timestamp_field) %}
    {%- if is_aggregate %}
    DELETE FROM {{ destination_table }}
        WHERE {{ timestamp_field }} >= DATEADD('SECOND', -MOD(DATE_PART(EPOCH_SECOND, TO_TIMESTAMP_NTZ('{{ start_time }}')), {{ 86400 if continuous else slide_interval.ToSeconds() }}), DATE_TRUNC('SECOND', TO_TIMESTAMP_NTZ('{{ start_time }}')))
        AND {{ timestamp_field }} < DATEADD('SECOND', -MOD(DATE_PART(EPOCH_SECOND, TO_TIMESTAMP_NTZ('{{ end_time }}')), {{ 86400 if continuous else slide_interval.ToSeconds() }}), DATE_TRUNC('SECOND', TO_TIMESTAMP_NTZ('{{ end_time }}')));
    {% else %}
    DELETE FROM {{ destination_table }}
        WHERE {{ timestamp_field }} >= TO_TIMESTAMP_NTZ('{{ start_time }}')
        AND {{ timestamp_field }} < TO_TIMESTAMP_NTZ('{{ end_time }}');
    {% endif %}
{%- endmacro %}
