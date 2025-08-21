{%- set separator = "__"  %}
{%- set effective_timestamp = "_EFFECTIVE_TIMESTAMP" %}

{%- macro rename_item_columns(join_keys, feature_timestamp_key, spine_timestamp_key, feature_columns, prefix) %}
    {{ feature_timestamp_key }} AS {{ spine_timestamp_key }},

    {%- for k, v in join_keys.items() %}
        {{ k }} AS {{ v }},
    {%- endfor %}

    {%- for col in feature_columns %}
        {{ col }} AS {{ prefix|upper }}{{ separator }}{{ col|upper }}{%- if not loop.last %}, {%- endif %}
    {%- endfor %}
{%- endmacro %}

{%- macro join(item, spine, spine_keys, spine_timestamp_key, include_feature_view_timestamp_columns) %}
    {%- set name = item.name %}
    {%- set data_delay = item.data_delay %}
    {%- set batch_schedule = item.batch_schedule %}
    {%- set feature_timestamp_key = item.timestamp_key %}
    {%- set feature_columns = item.features %}
    {%- set join_keys = item.join_keys %}
    {%- set ttl_seconds = item.ttl_seconds %}
    {%- set prefix = item.namespace %}
    {%- set all_join_keys = (join_keys.values()|list + [spine_timestamp_key])|join(", ") %}
    {%- set join_keys_list = (join_keys.values()|list)|join(", ") %}
    {%- set all_spine_join_keys = (spine_keys + [spine_timestamp_key])|join(", ") %}

    WITH
        {#-  Spine may contain duplicate join keys, we need to filter out the duplications. #}
        FILTERED_SPINE AS (
            SELECT DISTINCT {{ all_join_keys }}
            FROM {{ spine }}
        ),
        WITH_EFFECTIVE_TIMESTAMP AS (
            SELECT
                *,
                DATEADD('NANOSECOND', -MOD(DATE_PART(EPOCH_NANOSECOND, {{ feature_timestamp_key }}) - 1, {{ batch_schedule * 1_000_000_000 }}) + {{ batch_schedule * 1_000_000_000 }} + {{ data_delay * 1_000_000_000 }}, DATE_TRUNC('NANOSECOND', {{ feature_timestamp_key }})) AS {{ effective_timestamp }}
            FROM {{ name|upper }}_TABLE
        ),
        RENAMED AS (
            SELECT
                {{- rename_item_columns(join_keys, effective_timestamp, spine_timestamp_key, feature_columns, prefix) | indent(12)}}
            FROM WITH_EFFECTIVE_TIMESTAMP
        ),
        {#-  Filter the rows within the given ttl #}
        FILTERED AS (
            {#-  DISTINCT is needed if spine has duplicate join keys #}
            SELECT DISTINCT RENAMED.*
            FROM RENAMED
            INNER JOIN FILTERED_SPINE USING({{ join_keys_list }})
            WHERE RENAMED.{{ spine_timestamp_key }} >= DATEADD('SECOND', -{{ ttl_seconds }}, FILTERED_SPINE.{{ spine_timestamp_key }})
        ),
        OUTER_JOINED AS (
            SELECT
            {% if include_feature_view_timestamp_columns -%}
                {#-  Keep the feature timestamp separately to retrieve later #}
                FILTERED.{{ spine_timestamp_key }} AS {{ prefix|upper }}{{ separator }}{{ feature_timestamp_key|upper }},
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
                    LAST_VALUE({{ prefix|upper }}{{ separator }}{{ feature_timestamp_key|upper }}) IGNORE NULLS OVER (PARTITION BY {{ join_keys.keys()|join(", ") }} ORDER BY {{ spine_timestamp_key }} ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS {{ prefix|upper }}{{ separator }}{{ feature_timestamp_key|upper }},
                {%- endif -%}
                {%- for feature in feature_columns %}
                    LAST_VALUE({{ prefix|upper }}{{ separator }}{{ feature|upper }}) IGNORE NULLS OVER (PARTITION BY {{ join_keys.keys()|join(", ") }} ORDER BY {{ spine_timestamp_key }} ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS {{ prefix|upper }}{{ separator }}{{ feature|upper }}{% if not loop.last %},{% endif %}
                {%- endfor %}
            FROM OUTER_JOINED
        )
    SELECT DISTINCT
        {{ all_spine_join_keys }},
        {%- if include_feature_view_timestamp_columns -%}
            {{ prefix|upper }}{{ separator }}{{ feature_timestamp_key|upper }},
        {%- endif -%}
        {%- for feature in feature_columns %}
            {{ prefix|upper }}{{ separator }}{{ feature|upper }}{% if not loop.last %},{% endif %}
        {%- endfor %}
    FROM WINDOWED
    INNER JOIN {{ spine }} USING({{ all_join_keys }})
{%- endmacro %}

{%- macro aggregate_cte_name(prefix, spine, features, index) %}
    {%- if index < 0 %}{{ spine }}{% else %}{{ prefix|upper }}_{{ features[index].output_feature_name|upper }}_AGGREGATE_TABLE{% endif -%}
{% endmacro -%}

{%- macro join_window(item, spine, spine_keys, spine_timestamp_key) %}
    {%- set name = item.name %}
    {%- set feature_timestamp_key = item.timestamp_key %}
    {%- set feature_columns = item.features %}
    {%- set join_keys = item.join_keys %}
    {%- set time_aggregation = item.aggregation %}
    {%- set prefix = item.namespace %}
    {%- set slide_interval = time_aggregation.aggregation_slide_period.ToSeconds() %}
    {%- set join_key_list = join_keys.values()|list|join(", ")  %}
    {%- set all_join_keys = (join_keys.values()|list + [spine_timestamp_key])|join(", ") %}
    {%- set all_spine_join_keys = (spine_keys + [spine_timestamp_key])|join(", ") %}

    WITH
    RENAMED_{{ name|upper }} AS (
        SELECT
            {{- rename_item_columns(join_keys, feature_timestamp_key, spine_timestamp_key, [], prefix) | indent(12)}}
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
                {{ feature.output_feature_name|upper }} AS {{ prefix|upper }}{{ separator }}{{ feature.output_feature_name|upper }}
            FROM _SPINE_AGGREGATE_{{ name|upper }}
            INNER JOIN RENAMED_{{ name|upper }} USING ({{ all_join_keys }})
            GROUP BY {{ all_spine_join_keys }}, {{ prefix|upper }}{{ separator }}{{ feature.output_feature_name|upper }}
        ){%- if not loop.last %},{% endif %}
    {%- endfor -%}
    SELECT DISTINCT
        {{ all_spine_join_keys }},
        {%- for feature in time_aggregation.features %}
        {{ prefix|upper }}{{ separator }}{{ feature.output_feature_name|upper }}{%- if not loop.last %},{% endif %}
        {% endfor %}
    FROM _SPINE_AGGREGATE_{{ name|upper }}
    {%- for feature in time_aggregation.features %}
    INNER JOIN {{ aggregate_cte_name(name, spine, time_aggregation.features, loop.index0) }} USING ({{ all_join_keys }})
    {%- endfor -%}
{%- endmacro -%}

{%- macro fv_cte_name(name, suffix) %}
    _JOIN_{{ name|upper }}_TABLE_{{ suffix|upper }}
{%- endmacro %}

{%- macro final_select_name(name, replace_null, with_comma, new_name="") %}
    {%- if new_name|length == 0 -%}
        {%- set new_name = name  -%}
    {%- endif -%}
    {%- if replace_null %}
        ZEROIFNULL({{ name|upper }}) AS {{ new_name|upper }}
    {%- else %}
        {{ name|upper }} AS {{ new_name|upper }}
    {%- endif -%}
    {%- if with_comma %},{% endif -%}
{%- endmacro %}

{%- macro left_join(table_name, join_keys) %}
    LEFT JOIN {{ table_name }} USING ({{ join_keys }})
{%- endmacro %}
