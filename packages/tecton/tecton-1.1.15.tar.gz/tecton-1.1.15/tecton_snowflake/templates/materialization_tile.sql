{%- set join_key_list = join_keys|join(", ")  %}

{%- if continuous and not offline_materialization %}
WITH _SOURCE_WITH_TILE_TIME AS (
SELECT
    {{ timestamp_key }} AS _TILE_TIMESTAMP_KEY,
    *
FROM ({{ source }})
)
{% else %}
WITH _SOURCE_WITH_TILE_TIME AS (
    SELECT
        DATEADD('SECOND', -MOD(DATE_PART(EPOCH_SECOND, {{ timestamp_key }}), {{ 86400 if offline_materialization and continuous else slide_interval.ToSeconds() }}), DATE_TRUNC('SECOND', {{ timestamp_key }})) AS _TILE_TIMESTAMP_KEY,
        *
	FROM ({{ source }})
)
{% endif %}
SELECT
    {{ join_key_list }},
    {%- for column, functions in aggregations.items() -%}
        {%- for prefix, snowflake_function in functions %}
    	    {%- if prefix == "SUM_OF_SQUARES" %}
                SUM(SQUARE(CAST({{ column }} AS float))) AS {{ prefix }}_{{ column }},
            {%- elif prefix.startswith("LAST_NON_DISTINCT_N") %}
                {# TODO(TEC-10982): Refactor the aggregation struct passed into this template so function param can be handled appropriately. #}
                ARRAY_SLICE(ARRAYAGG({{ column }}) WITHIN GROUP ( ORDER BY {{ timestamp_key }} ASC ), -{{ snowflake_function }}, ARRAY_SIZE(ARRAYAGG({{ column }}))) AS {{ prefix }}_{{ column }},
            {%- elif prefix.startswith("FIRST_NON_DISTINCT_N") %}
                ARRAY_SLICE(ARRAYAGG({{ column }}) WITHIN GROUP ( ORDER BY {{ timestamp_key }} ASC ), 0, {{ snowflake_function }}) AS {{ prefix }}_{{ column }},
            {%- elif prefix != "ROW_NUMBER" %}
                {{ snowflake_function }}({{ column }}) AS {{ prefix }}_{{ column }},
            {%- endif %}
        {%- endfor %}
    {%- endfor %}
    _TILE_TIMESTAMP_KEY as {{ timestamp_key }}
FROM (
    _SOURCE_WITH_TILE_TIME
)
GROUP BY {{ join_key_list }}, _TILE_TIMESTAMP_KEY
