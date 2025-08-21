{%- set join_keys_list = join_keys|join(", ")  %}
{%- set slide_interval = aggregation.aggregation_slide_period.ToSeconds() %}
{%- set spine_timestamp_key = spine_timestamp_key or timestamp_key  %}
{%- set group_by_all_join_keys_list = (join_keys + ["_SPINE." + spine_timestamp_key])|join(", ") %}
{%- set using_all_join_keys_list = (join_keys + [spine_timestamp_key])|join(", ") %}
{%- set separator = "__"  %}

{%- macro final_select_name(name, replace_null, with_comma) %}
    {%- if replace_null %}
        coalesce({{ name|upper }}, 0) AS {{ name|upper }}
    {%- else %}
        {{ name|upper }}
    {%- endif -%}
    {%- if with_comma %},{% endif -%}
{%- endmacro %}

{%- macro aggregation_function(function, input_feature_name, output_feature_name) %}
    {%- if function == "AVG" %}
        SUM(pat.MEAN_{{ input_feature_name }} * pat.COUNT_{{ input_feature_name }}) / SUM(pat.COUNT_{{ input_feature_name }}) AS {{ output_feature_name }}
    {%- elif function == "COUNT" %}
        SUM(pat.{{ function }}_{{ input_feature_name }}) AS {{ output_feature_name }}
    {%- else %}
        {{ function }}(pat.{{ function }}_{{ input_feature_name }}) AS {{ output_feature_name }}
    {%- endif -%}
{%- endmacro %}

WITH _PARTIAL_AGGREGATION_TABLE AS (
    SELECT *,
    to_unixtime({{ timestamp_key }}) AS _ANCHOR_TIME
    FROM ({{ source }})
),
_SPINE AS (
    {%- if spine is not none %}
        SELECT DISTINCT
            {{ join_keys_list }},
            {{ spine_timestamp_key }},
            {%- if slide_interval > 0 %}
                {# Use the latest tile start time as _ANCHOR_TIME #}
                (to_unixtime({{ spine_timestamp_key }}) - {{ batch_schedule }} - MOD(to_unixtime({{ spine_timestamp_key }}), {{ slide_interval }})) AS "_ANCHOR_TIME"
            {%- else %}
                to_unixtime({{ spine_timestamp_key }}) AS "_ANCHOR_TIME"
            {%- endif %}

        FROM ({{ spine }})
    {%- else %}
        SELECT DISTINCT
            {{ join_keys_list }},
            {{ timestamp_key }},
            _ANCHOR_TIME

        FROM _PARTIAL_AGGREGATION_TABLE
    {%- endif %}
),
{%- for feature in aggregation.features %}
    {{ feature.output_feature_name|upper }}_TABLE AS (
        SELECT
            {{ join_keys_list }},
            _SPINE.{{ spine_timestamp_key }},
            {{ aggregation_function(feature.function|athena_function|upper, feature.input_feature_name|upper, feature.output_feature_name|upper) }}
        FROM _SPINE
        INNER JOIN _PARTIAL_AGGREGATION_TABLE pat USING ({{ join_keys_list }})
        {# Inclusive start time and exclusive end time. #}
        WHERE pat._ANCHOR_TIME <= _SPINE._ANCHOR_TIME + {{ feature.time_window.relative_time_window.window_end.ToSeconds() }}
        AND  pat._ANCHOR_TIME > _SPINE._ANCHOR_TIME + {{ feature.time_window.relative_time_window.window_start.ToSeconds() }}
        GROUP BY {{ group_by_all_join_keys_list }}
    ){%- if not loop.last %}, {% endif -%}
{%- endfor -%}
{# Band join all the feature tables at the end, select individual columns and replace null if needed #}
SELECT
    {{ join_keys_list }},
    {%- if spine is not none %}
        {# We need to keep the same timestamp to join later. #}
        {{ spine_timestamp_key }} AS {{ timestamp_key }},
    {%- else %}
        {# Tiles use the tile start time as the timestamp, for full aggregation we want the next tile start time as the timestamp value. #}
        DATE_ADD('SECOND', {{ slide_interval }}, {{ timestamp_key }}) AS {{ timestamp_key }},
    {%- endif %}
    {%- for feature in aggregation.features %}
        {{- final_select_name(feature.output_feature_name, feature.function|athena_function == "count", not loop.last) | indent }}
    {%- endfor -%}
    {# For each feature, do a band join against the rounded-off spine timestamp #}
FROM _SPINE
{%- for feature in aggregation.features %}
    LEFT JOIN {{ feature.output_feature_name|upper }}_TABLE USING ({{ using_all_join_keys_list }})
{%- endfor -%}
