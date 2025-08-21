{%- set start_time_defined = start_time is defined and start_time is not none  %}
{%- set end_time_defined = end_time is defined and end_time is not none  %}

SELECT * FROM (
    {{ source }}
)
{% if start_time_defined and end_time_defined %}
WHERE {{ timestamp_key }} >= TO_TIMESTAMP_NTZ('{{ start_time }}') AND {{ timestamp_key }} < TO_TIMESTAMP_NTZ('{{ end_time }}')
{% elif start_time_defined %}
WHERE {{ timestamp_key }} >= TO_TIMESTAMP_NTZ('{{ start_time }}')
{% elif end_time_defined %}
WHERE {{ timestamp_key }} < TO_TIMESTAMP_NTZ('{{ end_time }}')
{% endif %}
