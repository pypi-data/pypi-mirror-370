{#-  Register inputted transformation SQL statements as CTEs #}
{%- if inputs|length > 0 %}
WITH
{% endif -%}
{%- for input in inputs -%}
    {{ input.name }} AS ({{ input.sql_str }}){%- if not loop.last %}, {% endif -%}
{%- endfor %}
SELECT * FROM (
    {{ user_function }}
)
