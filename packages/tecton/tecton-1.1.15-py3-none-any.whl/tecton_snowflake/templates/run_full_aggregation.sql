{%- set join_keys_list = join_keys|join(", ")  %}
{%- set slide_interval = aggregation.aggregation_slide_period.ToSeconds() %}
{%- set spine_timestamp_key = spine_timestamp_key or timestamp_key  %}
{%- set all_join_keys_list = (join_keys + [spine_timestamp_key])|join(", ") %}
{%- set separator = "__"  %}

{%- macro final_select_name(name, replace_null, with_comma) %}
    {%- if replace_null %}
        ZEROIFNULL({{ name|upper }}) AS {{ name|upper }}
    {%- else %}
        {{ name|upper }}
    {%- endif -%}
    {%- if with_comma %},{% endif -%}
{%- endmacro %}

{%- macro aggregation_function(function, input_feature_name, output_feature_name) %}
    {%- if function == "AVG" %}
        SUM(MEAN_{{ input_feature_name }} * COUNT_{{ input_feature_name }}) / SUM(COUNT_{{ input_feature_name }}) AS {{ output_feature_name }}
    {%- elif function == "COUNT" %}
        SUM({{ function }}_{{ input_feature_name }}) AS {{ output_feature_name }}
    {%- elif function == "VAR_SAMP" %}
        {# sample variation equation: (Σ(x^2) - (Σ(x)^2)/N)/N-1 #}
        (SUM(SUM_OF_SQUARES_{{ input_feature_name }}) - SQUARE(SUM(SUM_{{ input_feature_name }})) / SUM(COUNT_{{ input_feature_name }})) / NULLIFZERO((SUM(COUNT_{{ input_feature_name }}) - 1)) AS {{ output_feature_name }}
    {%- elif function == "VAR_POP" %}
        {# population variation equation: Σ(x^2)/n - μ^2 #}
        SUM(SUM_OF_SQUARES_{{ input_feature_name }}) / SUM(COUNT_{{ input_feature_name }}) - SQUARE(SUM(SUM_{{ input_feature_name }}) / SUM(COUNT_{{ input_feature_name }})) AS {{ output_feature_name }}
    {%- elif function == "STDDEV_SAMP" %}
        {# sample standard deviation equation: √ ((Σ(x^2) - (Σ(x)^2)/N)/N-1) #}
        SQRT((SUM(SUM_OF_SQUARES_{{ input_feature_name }}) - SQUARE(SUM(SUM_{{ input_feature_name }})) / SUM(COUNT_{{ input_feature_name }})) / NULLIFZERO((SUM(COUNT_{{ input_feature_name }}) - 1))) AS {{ output_feature_name }}
    {%- elif function == "STDDEV_POP" %}
        {# population standard deviation equation: √ (Σ(x^2)/n - μ^2) #}
        SQRT(SUM(SUM_OF_SQUARES_{{ input_feature_name }}) / SUM(COUNT_{{ input_feature_name }}) - SQUARE(SUM(SUM_{{ input_feature_name }}) / SUM(COUNT_{{ input_feature_name }}))) AS {{ output_feature_name }}
    {%- else %}
        {{ function }}({{ function }}_{{ input_feature_name }}) AS {{ output_feature_name }}
    {%- endif -%}
{%- endmacro %}

{%- macro create_first_or_last_non_distinct_n_table(spine_timestamp_key,join_keys_list,feature,truncate_from_left) %}
    SELECT
        {{ join_keys_list }},
        _SPINE.{{spine_timestamp_key}},
        {%- if truncate_from_left %}
            ARRAY_SLICE(ARRAYAGG(VALUE) WITHIN GROUP( ORDER BY _PARTIAL_AGGREGATION_TABLE._ANCHOR_TIME,INDEX), -{{ feature.function_params.last_n.n }}, ARRAY_SIZE(ARRAYAGG(VALUE))) AS {{ feature.output_feature_name }}
        {%- else %}
            ARRAY_SLICE(ARRAYAGG(VALUE) WITHIN GROUP (ORDER BY _PARTIAL_AGGREGATION_TABLE._ANCHOR_TIME,INDEX), 0, {{ feature.function_params.first_n.n }}) AS {{ feature.output_feature_name }}
        {%- endif %}
    FROM _SPINE
	INNER JOIN _PARTIAL_AGGREGATION_TABLE USING ({{ join_keys_list }}),
    {%- if truncate_from_left %}
        LATERAL FLATTEN(input=>LAST_NON_DISTINCT_N{%- if not is_continuous -%}{{feature.function_params.last_n.n}}{%- endif -%}_{{ feature.input_feature_name }})
    {%- else %}
        LATERAL FLATTEN(input=>FIRST_NON_DISTINCT_N{%- if not is_continuous -%}{{feature.function_params.first_n.n}}{%- endif -%}_{{ feature.input_feature_name }})
    {%- endif %}
    WHERE _SPINE._ANCHOR_TIME >= _PARTIAL_AGGREGATION_TABLE._ANCHOR_TIME
    AND   _SPINE._ANCHOR_TIME <  _PARTIAL_AGGREGATION_TABLE._ANCHOR_TIME + {{ feature.window.ToSeconds() }}
    GROUP BY {{ all_join_keys_list }}
{%- endmacro %}

WITH _PARTIAL_AGGREGATION_TABLE AS (
    SELECT *,
    DATE_PART(EPOCH_SECOND, DATEADD(SECOND, {{ data_delay }}, {{ timestamp_key }})) AS _ANCHOR_TIME
    FROM ({{ source }})
),
_SPINE AS (
    SELECT DISTINCT
        {{ join_keys_list }},
        {{ spine_timestamp_key }},
        {%- if spine is not none %}
            (DATE_PART(EPOCH_SECOND, {{ spine_timestamp_key }}) - {{ batch_schedule }}) AS _ANCHOR_TIME
            FROM ({{ spine }})
        {%- else %}
            _ANCHOR_TIME
            {# TODO(TEC-8312): Full aggregation won't output all the possible time windows. It will use rows in the data source as the spine. #}
            FROM _PARTIAL_AGGREGATION_TABLE
        {%- endif %}
),
{%- for feature in aggregation.features %}
    {{ feature.output_feature_name|upper }}_TABLE AS (
        {%- if feature.function|snowflake_function == "last_non_distinct_n"%}
            {{ create_first_or_last_non_distinct_n_table(spine_timestamp_key,join_keys_list,feature,True) }}
        {%- elif feature.function|snowflake_function == "first_non_distinct_n"%}
            {{ create_first_or_last_non_distinct_n_table(spine_timestamp_key,join_keys_list,feature,False) }}
        {%- else %}
            SELECT
                {{ join_keys_list }},
                _SPINE.{{ spine_timestamp_key }},
                {{ aggregation_function(feature.function|snowflake_function|upper, feature.input_feature_name|upper, feature.output_feature_name|upper) }}
            FROM _SPINE
            INNER JOIN _PARTIAL_AGGREGATION_TABLE USING ({{ join_keys_list }})
            {# Inclusive start time and exclusive end time. #}
            WHERE _SPINE._ANCHOR_TIME >= _PARTIAL_AGGREGATION_TABLE._ANCHOR_TIME
            AND   _SPINE._ANCHOR_TIME <  _PARTIAL_AGGREGATION_TABLE._ANCHOR_TIME + {{ feature.window.ToSeconds() }}
            GROUP BY {{ all_join_keys_list }}
        {%- endif %}
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
        DATEADD('SECOND', {{ slide_interval }}, DATE_TRUNC('SECOND', {{ timestamp_key }})) AS {{ timestamp_key }},
    {%- endif %}
    {%- for feature in aggregation.features %}
        {{- final_select_name(feature.output_feature_name, feature.function|snowflake_function == "count", not loop.last) | indent }}
    {%- endfor -%}
    {# For each feature, do a band join against the rounded-off spine timestamp #}
FROM _SPINE
{%- for feature in aggregation.features %}
    LEFT JOIN {{ feature.output_feature_name|upper }}_TABLE USING ({{ all_join_keys_list }})
{%- endfor -%}
