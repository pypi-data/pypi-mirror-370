{#-  Register data source sql as CTE #}
{%- if data_sources|length > 0 %}
WITH
{%- endif %}
{%- for name, sql_str in data_sources.items() %}
    {{ name }} AS ({{ sql_str }}){%- if not loop.last %}, {%- endif %}
{%- endfor %}
SELECT * FROM ({{ source }})
