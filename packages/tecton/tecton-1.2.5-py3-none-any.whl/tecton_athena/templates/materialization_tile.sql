{%- set join_key_list = join_keys|join(", ")  %}
WITH _SOURCE_WITH_TILE_TIME AS (
    SELECT
        DATE_ADD('SECOND', -MOD(to_unixtime({{ timestamp_key }}), {{ slide_interval.ToSeconds() }}), {{ timestamp_key }}) AS _TILE_TIMESTAMP_KEY,
        *
    FROM ({{ source }})
)
SELECT
    {{ join_key_list }},
    {%- for column, functions in aggregations.items() -%}
        {%- for prefix, athena_function in functions %}
            {{ athena_function }}({{ column }}) AS {{ prefix }}_{{ column }},
        {%- endfor %}
    {%- endfor %}
    _TILE_TIMESTAMP_KEY as {{ timestamp_key }}
FROM (
    _SOURCE_WITH_TILE_TIME
)
GROUP BY {{ join_key_list }}, _TILE_TIMESTAMP_KEY
