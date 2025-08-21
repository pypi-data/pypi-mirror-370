{% import "historical_features_macros.sql" as macros %}

CREATE OR REPLACE TEMPORARY {{view_or_table}} {{ macros.fv_cte_name(item.name, suffix) }} AS (
    WITH
        {{ item.name|upper }}_TABLE AS ({{ item.sql }}),
        _FEATURE_TABLE AS ({{- macros.join(item, spine_table_name, spine_keys, spine_timestamp_key, include_feature_view_timestamp_columns)}})
    SELECT * FROM _FEATURE_TABLE
)
