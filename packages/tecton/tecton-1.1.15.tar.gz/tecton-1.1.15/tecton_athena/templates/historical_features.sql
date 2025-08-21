{%- set separator = "__"  %}
{%- set all_spine_join_keys = (spine_keys + [spine_timestamp_key])|join(", ") %}

{%- macro rename_item_columns(join_keys, feature_timestamp_key, spine_timestamp_key, feature_columns, prefix) %}
    {{ feature_timestamp_key }} AS {{ spine_timestamp_key }},

    {%- for k, v in join_keys.items() %}
        {{ k }} AS {{ v }},
    {%- endfor %}

    {%- for col in feature_columns %}
        {{ col }} AS {{ prefix|upper }}{{ separator }}{{ col|upper }}{%- if not loop.last %}, {%- endif %}
    {%- endfor %}
{%- endmacro %}

{%- macro join(name, spine, spine_timestamp_key, feature_timestamp_key, feature_columns, join_keys, ttl_seconds) %}
    {%- set all_join_keys = (join_keys.values()|list + [spine_timestamp_key])|join(", ") %}
    {%- set join_keys_list = (join_keys.values()|list)|join(", ") %}
    WITH
        {#-  Spine may contain duplicate join keys, we need to filter out the duplications. #}
        FILTERED_SPINE AS (
            SELECT DISTINCT {{ all_join_keys }}
            FROM {{ spine }}
        ),
        RENAMED AS (
            SELECT
                {{- rename_item_columns(join_keys, feature_timestamp_key, spine_timestamp_key, feature_columns, name) | indent(12)}}
            FROM {{ name|upper }}_TABLE
        ),
        {#-  Filter the rows within the given ttl #}
        FILTERED AS (
            {#-  DISTINCT is needed if spine has duplicate join keys #}
            SELECT DISTINCT {{ join_keys_list }}, RENAMED.*
            FROM RENAMED
            INNER JOIN FILTERED_SPINE USING({{ join_keys_list }})
            WHERE RENAMED.{{ spine_timestamp_key }} >= DATE_ADD('SECOND', -{{ ttl_seconds }}, FILTERED_SPINE.{{ spine_timestamp_key }})
        ),
        OUTER_JOINED AS (
            SELECT
            {% if include_feature_view_timestamp_columns -%}
                {#-  Keep the feature timestamp separately to retrieve later #}
                FILTERED.{{ spine_timestamp_key }} AS {{ name|upper }}{{ separator }}{{ feature_timestamp_key|upper }},
            {%- endif -%}
            *
            FROM FILTERED
            FULL JOIN FILTERED_SPINE USING({{ all_join_keys }})
        ),
        {#-  This window function will take the most recent value that is no later than the spine timestamp for every column #}
        WINDOWED AS (
            SELECT
                {{ all_join_keys }},
                {%- if include_feature_view_timestamp_columns -%}
                    LAST_VALUE({{ name|upper }}{{ separator }}{{ feature_timestamp_key|upper }}) IGNORE NULLS OVER (PARTITION BY {{ join_keys.keys()|join(", ") }} ORDER BY {{ spine_timestamp_key }} ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS {{ name|upper }}{{ separator }}{{ feature_timestamp_key|upper }},
                {%- endif -%}
                {%- for feature in feature_columns %}
                    LAST_VALUE({{ name|upper }}{{ separator }}{{ feature|upper }}) IGNORE NULLS OVER (PARTITION BY {{ join_keys.keys()|join(", ") }} ORDER BY {{ spine_timestamp_key }} ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS {{ name|upper }}{{ separator }}{{ feature|upper }}{% if not loop.last %},{% endif %}
                {%- endfor %}
            FROM OUTER_JOINED
        )
    SELECT DISTINCT
        {{ all_spine_join_keys }},
        {%- if include_feature_view_timestamp_columns -%}
            {{ name|upper }}{{ separator }}{{ feature_timestamp_key|upper }},
        {%- endif -%}
        {%- for feature in feature_columns %}
            {{ name|upper }}{{ separator }}{{ feature|upper }}{% if not loop.last %},{% endif %}
        {%- endfor %}
    FROM WINDOWED
    INNER JOIN {{ spine }} USING({{ all_join_keys }})
{%- endmacro %}

{%- macro aggregate_cte_name(prefix, spine, features, index) %}
    {%- if index < 0 %}{{ spine }}{% else %}{{ prefix|upper }}_{{ features[index].output_feature_name|upper }}_AGGREGATE_TABLE{% endif -%}
{% endmacro -%}

{%- macro join_window(name, spine, spine_timestamp_key, feature_timestamp_key, feature_columns, join_keys, time_aggregation, last_join) %}
    {%- set slide_interval = time_aggregation.aggregation_slide_period.ToSeconds() %}
    {%- set join_key_list = join_keys.values()|list|join(", ")  %}
    {%- set all_join_keys = (join_keys.values()|list + [spine_timestamp_key])|join(", ") %}
    RENAMED_{{ name|upper }} AS (
        SELECT
            {{- rename_item_columns(join_keys, feature_timestamp_key, spine_timestamp_key, [], name) | indent(12)}}
            {%- for feature in time_aggregation.features %}
                {{ feature.output_feature_name|upper }}{%- if not loop.last %},{% endif %}
            {%- endfor %}
        FROM {{ name|upper }}_TABLE
    ),
    _SPINE_AGGREGATE_{{ name|upper }} AS (
        SELECT DISTINCT
            {{ all_spine_join_keys }}
            FROM {{ spine }}
    ),
    {# For each feature, do a band join against the rounded-off spine timestamp #}
    {%- for feature in time_aggregation.features %}
        {{ aggregate_cte_name(name, spine, time_aggregation.features, loop.index0) }} AS (
            SELECT DISTINCT
                {{ all_spine_join_keys }},
                {# There should be at most 1 value for each join keys #}
                {{ feature.output_feature_name|upper }} AS {{ name|upper }}{{ separator }}{{ feature.output_feature_name|upper }}
            FROM _SPINE_AGGREGATE_{{ name|upper }}
            INNER JOIN RENAMED_{{ name|upper }} USING ({{ all_join_keys }})
            GROUP BY {{ all_spine_join_keys }}, {{ feature.output_feature_name|upper }}
        ){%- if not (loop.last and last_join) %}, {% endif -%}
    {%- endfor -%}
{%- endmacro -%}

{%- macro fv_cte_name(items, index) %}
    {%- if index < 0 %}_TT_SPINE_TABLE{% else %}_JOIN_{{ items[index].name|upper }}_TABLE{% endif -%}
{%- endmacro %}

{%- macro final_select_name(name, replace_null, with_comma) %}
    {%- if replace_null %}
        coalesce({{ name|upper }}, 0) AS {{ name|upper }}
    {%- else %}
        {{ name|upper }}
    {%- endif -%}
    {%- if with_comma %},{% endif -%}
{%- endmacro %}

{%- macro left_join(table_name, join_keys) %}
    LEFT JOIN {{ table_name }} USING ({{ join_keys }})
{%- endmacro %}

WITH
    _TT_SPINE_TABLE AS ({{ spine_sql }}){%- if feature_set_items|length > 0 %},{%- endif -%}
    {%- for item in feature_set_items %}
        {{ item.name|upper }}_TABLE AS ({{ item.sql }}),
    {%- endfor %}
    {%- for item in feature_set_items %}
        {%- if item.aggregation %}
            {{- join_window(item.name, "_TT_SPINE_TABLE", spine_timestamp_key, item.timestamp_key, item.features, item.join_keys, item.aggregation, loop.last) | indent }}
        {% else %}
            {{ fv_cte_name(feature_set_items, loop.index0) }} AS (
                {{- join(item.name, "_TT_SPINE_TABLE", spine_timestamp_key, item.timestamp_key, item.features, item.join_keys, item.ttl_seconds) | indent }}
            ){%- if not loop.last -%}, {% endif -%}
        {% endif -%}
    {%- endfor -%}
{# Band join all the feature tables at the end, select individual columns and replace null if needed #}
SELECT DISTINCT
    {%- if feature_set_items|length > 0 %}
        {{ all_spine_join_keys }}
        {%- if spine_contains_non_join_keys %},_TT_SPINE_TABLE.*{%- endif -%},
        {%- if include_feature_view_timestamp_columns -%}
            {%- for item in feature_set_items -%}
                {%- if item.aggregation -%}
                    {# Use the closest recent tile start time as the feature timestamp for aggregation features #}
                    {%- if item.aggregation.aggregation_slide_period.ToSeconds() > 0 -%}
                        DATE_ADD('SECOND', -MOD(DATE_PART(EPOCH_SECOND, _TT_SPINE_TABLE.{{ spine_timestamp_key }}), {{ item.aggregation.aggregation_slide_period.ToSeconds() }}), _TT_SPINE_TABLE.{{ spine_timestamp_key }}) AS "{{ final_select_name(item.name + separator + item.timestamp_key, false, true) }}"
                    {%- else %}
                        _TT_SPINE_TABLE.{{ spine_timestamp_key }} AS "{{ final_select_name(item.name + separator + item.timestamp_key, false, true) }}"
                    {%- endif -%}
                {%- else %}
                    {{ final_select_name(item.name + separator + item.timestamp_key, false, true) }}
                {%- endif -%}
            {%- endfor %}
        {%- endif -%}
        {%- for item in feature_set_items -%}
            {%- set last_item = loop.last -%}
            {%- if item.aggregation -%}
                {%- for feature in item.aggregation.features %}
                    {{- final_select_name(item.name + separator + feature.output_feature_name, feature.function|athena_function == "count", not (loop.last and last_item)) | indent }}
                {%- endfor -%}
            {%- else %}
                {%- for feature in item.features %}
                    {{- final_select_name(item.name + separator + feature, false, not (loop.last and last_item)) | indent }}
                {%- endfor -%}
            {%- endif -%}
        {%- endfor %}
    {%- else %}
        _TT_SPINE_TABLE.*
    {%- endif %}
FROM _TT_SPINE_TABLE
{%- for item in feature_set_items -%}
    {%- if item.aggregation -%}
        {%- for feature in item.aggregation.features %}
            {{- left_join(aggregate_cte_name(item.name, "_TT_SPINE_TABLE", item.aggregation.features, loop.index0), all_spine_join_keys) -}}
        {%- endfor -%}
    {%- else %}
        {{- left_join(fv_cte_name(feature_set_items, loop.index0), all_spine_join_keys) -}}
    {%- endif -%}
{%- endfor -%}
