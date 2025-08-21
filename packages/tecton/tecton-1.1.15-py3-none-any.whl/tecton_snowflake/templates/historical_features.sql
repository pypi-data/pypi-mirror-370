{% import "historical_features_macros.sql" as macros %}

{%- set separator = "__"  %}
{%- set all_spine_join_keys = (spine_keys + [spine_timestamp_key])|join(", ") %}

{%- if not use_temp_tables %}
WITH
    {{ spine_table_name }} AS ({{ spine_sql }}){%- if feature_set_items|length > 0 and not use_temp_tables %},{%- endif -%}
        {%- for item in feature_set_items %}
            {{ item.name|upper }}_TABLE AS ({{ item.sql }}),
        {%- endfor %}
        {%- for item in feature_set_items %}
            {%- if item.aggregation %}
                {{ macros.fv_cte_name(feature_set_items[loop.index0].name, suffix) }} AS (
                    {{- macros.join_window(item, spine_table_name, spine_keys, spine_timestamp_key) | indent }}
                ){%- if not loop.last -%},{% endif -%}
            {% else %}
                {{ macros.fv_cte_name(feature_set_items[loop.index0].name, suffix) }} AS (
                    {{- macros.join(item, spine_table_name, spine_keys, spine_timestamp_key, include_feature_view_timestamp_columns) | indent }}
                ){%- if not loop.last -%},{% endif -%}
            {% endif -%}
        {%- endfor -%}
{%- endif -%}
{# Band join all the feature tables at the end, select individual columns and replace null if needed #}
SELECT
    {{ spine_table_name }}.*{%- if feature_set_items|length > 0 %},{%- endif -%}
    {%- if include_feature_view_timestamp_columns -%}
        {%- for item in feature_set_items -%}
            {%- if item.aggregation -%}
                {# Use the closest recent tile start time as the feature timestamp for aggregation features #}
                DATEADD('SECOND', -MOD(DATE_PART(EPOCH_SECOND, {{ spine_table_name }}.{{ spine_timestamp_key }}), {{ item.aggregation.aggregation_slide_period.ToSeconds() }}), DATE_TRUNC('SECOND', {{ spine_table_name }}.{{ spine_timestamp_key }})) AS {{ item.name|upper + separator + item.timestamp_key|upper }},
            {%- else %}
                {{ macros.final_select_name(item.namespace + separator + item.timestamp_key, false, true) }}
            {%- endif -%}
        {%- endfor %}
    {%- endif -%}
    {%- for item in feature_set_items -%}
        {%- set last_item = loop.last -%}
        {%- if item.aggregation -%}
            {%- for feature in item.aggregation.features %}
                {{- macros.final_select_name(item.namespace + separator + feature.output_feature_name, feature.function|snowflake_function == "count", not (loop.last and last_item), ("" if item.append_prefix else feature.output_feature_name)) | indent }}
            {%- endfor -%}
        {%- else %}
            {%- for feature in item.features %}
                {{- macros.final_select_name(item.namespace + separator + feature, false, not (loop.last and last_item), ("" if item.append_prefix else feature)) | indent }}
            {%- endfor -%}
        {%- endif -%}
    {%- endfor %}
FROM {{ spine_table_name }}
{%- for item in feature_set_items -%}
    {{- macros.left_join(macros.fv_cte_name(item.name, suffix), all_spine_join_keys) -}}
{%- endfor -%}
