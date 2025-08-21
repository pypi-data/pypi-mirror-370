{%- set join_key_list = join_keys|join(", ")  %}

SELECT
    {{ join_key_list }},
    {%- for column, functions in aggregations.items() -%}
        {%- for function, snowflake_function in functions %}
            {%- if function != "ROW_NUMBER" -%}
                {{ function }}_{{ column }} AS {{ column }}_{{ function }}_{{ slide_interval_string }},
            {%- endif -%}
        {%- endfor %}
    {%- endfor %}
    {{ timestamp_key }} AS TILE_START_TIME,
    DATEADD('SECOND', {{ slide_interval.ToSeconds() }}, {{ timestamp_key }}) AS TILE_END_TIME
FROM (
    {{ source }}
)
